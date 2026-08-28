from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from database import get_connection

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


app = Flask(__name__)

app.secret_key = "smart-voting-secret-key"


# =================================================
# HOME
# =================================================

@app.route("/")
def index():
    return render_template("index.html")


# =================================================
# VOTER REGISTRATION
# AUTOMATIC DOCUMENT VERIFICATION
# =================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get("full_name")
        email = request.form.get("email")
        voter_number = request.form.get("voter_number")
        dob = request.form.get("dob")
        aadhaar_number = request.form.get("aadhaar_number")
        pan_number = request.form.get("pan_number")
        password = request.form.get("password")

        if not all([
            full_name,
            email,
            voter_number,
            dob,
            aadhaar_number,
            pan_number,
            password
        ]):
            flash(
                "Please fill all required fields.",
                "danger"
            )

            return redirect(url_for("register"))

        pan_number = pan_number.upper()

        connection = get_connection()
        cursor = connection.cursor()

        try:

            # =================================================
            # 1. CHECK VERIFICATION RECORD
            # =================================================

            cursor.execute(
                """
                SELECT
                    full_name,
                    dob,
                    aadhaar_number,
                    pan_number,
                    verification_status
                FROM verification_records
                WHERE voter_number = %s
                """,
                (voter_number,)
            )

            record = cursor.fetchone()

            if record is None:

                flash(
                    "Voter ID not found in verification database.",
                    "danger"
                )

                return redirect(url_for("register"))

            stored_name = record[0]
            stored_dob = record[1]
            stored_aadhaar = record[2]
            stored_pan = record[3]
            verification_status = record[4]

            # =================================================
            # 2. NAME VERIFICATION
            # =================================================

            if full_name.strip().lower() != stored_name.strip().lower():

                flash(
                    "Verification failed: Name does not match.",
                    "danger"
                )

                return redirect(url_for("register"))

            # =================================================
            # 3. DOB VERIFICATION
            # =================================================

            if hasattr(stored_dob, "strftime"):
                stored_dob = stored_dob.strftime("%Y-%m-%d")

            dob = dob.strip()

            if dob != stored_dob:

                flash(
                    "Verification failed: Date of Birth does not match.",
                    "danger"
                )

                return redirect(url_for("register"))

            # =================================================
            # 4. AADHAAR VERIFICATION
            # =================================================

            if str(aadhaar_number).strip() != str(stored_aadhaar).strip():

                flash(
                    "Verification failed: Aadhaar Number does not match.",
                    "danger"
                )

                return redirect(url_for("register"))

            # =================================================
            # 5. PAN VERIFICATION
            # =================================================

            if pan_number != str(stored_pan).upper():

                flash(
                    "Verification failed: PAN Number does not match.",
                    "danger"
                )

                return redirect(url_for("register"))

            # =================================================
            # 6. VERIFICATION STATUS
            # =================================================

            if str(verification_status).lower() != "verified":

                flash(
                    "Verification record is not verified.",
                    "warning"
                )

                return redirect(url_for("register"))

            # =================================================
            # 7. CHECK EMAIL ALREADY EXISTS
            # =================================================

            cursor.execute(
                """
                SELECT voter_id
                FROM voters
                WHERE email = %s
                """,
                (email,)
            )

            if cursor.fetchone() is not None:

                flash(
                    "This email is already registered.",
                    "danger"
                )

                return redirect(url_for("register"))

            # =================================================
            # 8. CHECK VOTER NUMBER ALREADY EXISTS
            # =================================================

            cursor.execute(
                """
                SELECT voter_id
                FROM voters
                WHERE voter_number = %s
                """,
                (voter_number,)
            )

            if cursor.fetchone() is not None:

                flash(
                    "This Voter ID is already registered.",
                    "danger"
                )

                return redirect(url_for("register"))

            # =================================================
            # 9. PASSWORD HASH
            # =================================================

            hashed_password = generate_password_hash(password)

            # =================================================
            # 10. INSERT VOTER
            # =================================================

            cursor.execute(
                """
                INSERT INTO voters
                (
                    full_name,
                    email,
                    password,
                    voter_number,
                    dob,
                    aadhaar_number,
                    pan_number,
                    document_verified,
                    status
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    TRUE,
                    'Pending'
                )
                """,
                (
                    full_name,
                    email,
                    hashed_password,
                    voter_number,
                    dob,
                    aadhaar_number,
                    pan_number
                )
            )

            connection.commit()

            flash(
                "Registration successful! Documents verified. Waiting for admin approval.",
                "success"
            )

            return redirect(url_for("login"))

        except Exception as error:

            connection.rollback()

            print("Registration Error:", error)

            flash(
                "Registration failed. Please check your details.",
                "danger"
            )

            return redirect(url_for("register"))

        finally:

            cursor.close()
            connection.close()

    return render_template("register.html")


# =================================================
# VOTER LOGIN
# =================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        # FIXED: use get() instead of request.form["email"]
        email = request.form.get("email")
        password = request.form.get("password")

        # Check empty fields

        if not email or not password:

            flash(
                "Email and Password are required.",
                "danger"
            )

            return redirect(url_for("login"))

        connection = get_connection()
        cursor = connection.cursor()

        try:

            cursor.execute(
                """
                SELECT
                    voter_id,
                    full_name,
                    password,
                    status,
                    document_verified
                FROM voters
                WHERE email = %s
                """,
                (email,)
            )

            voter = cursor.fetchone()

        except Exception as error:

            print("Login Database Error:", error)

            flash(
                "Unable to login. Please try again.",
                "danger"
            )

            return redirect(url_for("login"))

        finally:

            cursor.close()
            connection.close()

        # =================================================
        # CHECK USER
        # =================================================

        if voter is None:

            flash(
                "Invalid email or password.",
                "danger"
            )

            return redirect(url_for("login"))

        # =================================================
        # CHECK PASSWORD
        # =================================================

        try:

            password_correct = check_password_hash(
                voter[2],
                password
            )

        except Exception:

            password_correct = False

        if not password_correct:

            flash(
                "Invalid email or password.",
                "danger"
            )

            return redirect(url_for("login"))

        # =================================================
        # CHECK DOCUMENT
        # =================================================

        if not voter[4]:

            flash(
                "Your documents are not verified.",
                "warning"
            )

            return redirect(url_for("login"))

        # =================================================
        # CHECK ADMIN APPROVAL
        # =================================================

        if str(voter[3]).lower() != "approved":

            flash(
                "Your account is waiting for admin approval.",
                "warning"
            )

            return redirect(url_for("login"))

        # =================================================
        # CREATE SESSION
        # =================================================

        session["voter_id"] = voter[0]
        session["voter_name"] = voter[1]

        return redirect(
            url_for("voter_dashboard")
        )

    return render_template("login.html")


# =================================================
# VOTER DASHBOARD
# =================================================

@app.route("/dashboard")
def voter_dashboard():

    if "voter_id" not in session:

        return redirect(
            url_for("login")
        )

    return render_template(
        "voter_dashboard.html",
        name=session["voter_name"]
    )


# =================================================
# CANDIDATES
# =================================================

@app.route("/candidates")
def candidates():

    if "voter_id" not in session:

        return redirect(
            url_for("login")
        )

    voter_id = session["voter_id"]

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT
                candidate_id,
                candidate_name,
                party_name,
                symbol
            FROM candidates
            ORDER BY candidate_id
            """
        )

        candidates_data = cursor.fetchall()

        # Check whether already voted

        cursor.execute(
            """
            SELECT vote_id
            FROM votes
            WHERE voter_id = %s
            """,
            (voter_id,)
        )

        already_voted = cursor.fetchone() is not None

    finally:

        cursor.close()
        connection.close()

    return render_template(
        "candidates.html",
        candidates=candidates_data,
        already_voted=already_voted
    )


# =================================================
# VOTE
# ONE VOTER = ONE VOTE
# =================================================

@app.route(
    "/vote/<int:candidate_id>",
    methods=["POST"]
)
def vote(candidate_id):

    if "voter_id" not in session:

        return redirect(
            url_for("login")
        )

    voter_id = session["voter_id"]

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # =================================================
        # CHECK ALREADY VOTED
        # =================================================

        cursor.execute(
            """
            SELECT vote_id
            FROM votes
            WHERE voter_id = %s
            """,
            (voter_id,)
        )

        if cursor.fetchone():

            flash(
                "You have already voted. One voter can vote only once.",
                "warning"
            )

            return redirect(
                url_for("candidates")
            )

        # =================================================
        # CHECK CANDIDATE EXISTS
        # =================================================

        cursor.execute(
            """
            SELECT candidate_id
            FROM candidates
            WHERE candidate_id = %s
            """,
            (candidate_id,)
        )

        candidate = cursor.fetchone()

        if candidate is None:

            flash(
                "Candidate not found.",
                "danger"
            )

            return redirect(
                url_for("candidates")
            )

        # =================================================
        # SAVE VOTE
        # =================================================

        cursor.execute(
            """
            INSERT INTO votes
            (
                voter_id,
                candidate_id
            )
            VALUES
            (
                %s,
                %s
            )
            """,
            (
                voter_id,
                candidate_id
            )
        )

        connection.commit()

        flash(
            "Your vote has been recorded successfully.",
            "success"
        )

        return redirect(
            url_for("result")
        )

    except Exception as error:

        connection.rollback()

        print("Vote Error:", error)

        flash(
            "Vote could not be recorded.",
            "danger"
        )

        return redirect(
            url_for("candidates")
        )

    finally:

        cursor.close()
        connection.close()


# =================================================
# RESULT
# =================================================

@app.route("/result")
def result():

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT
                c.candidate_name,
                c.party_name,
                c.symbol,
                COUNT(v.vote_id)
            FROM candidates c
            LEFT JOIN votes v
                ON c.candidate_id = v.candidate_id
            GROUP BY
                c.candidate_id,
                c.candidate_name,
                c.party_name,
                c.symbol
            ORDER BY COUNT(v.vote_id) DESC
            """
        )

        results = cursor.fetchall()

    finally:

        cursor.close()
        connection.close()

    return render_template(
        "result.html",
        results=results
    )


# =================================================
# ADMIN LOGIN
# =================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:

            flash(
                "Username and Password are required.",
                "danger"
            )

            return redirect(
                url_for("admin_login")
            )

        connection = get_connection()
        cursor = connection.cursor()

        try:

            cursor.execute(
                """
                SELECT
                    admin_id,
                    username,
                    password
                FROM admins
                WHERE username = %s
                """,
                (username,)
            )

            admin = cursor.fetchone()

        finally:

            cursor.close()
            connection.close()

        if admin is None or admin[2] != password:

            flash(
                "Invalid admin login.",
                "danger"
            )

            return redirect(
                url_for("admin_login")
            )

        session["admin_id"] = admin[0]
        session["admin_username"] = admin[1]

        return redirect(
            url_for("admin_dashboard")
        )

    return render_template(
        "admin_login.html"
    )


# =================================================
# ADMIN DASHBOARD
# =================================================

@app.route("/admin/dashboard")
def admin_dashboard():

    if "admin_id" not in session:

        return redirect(
            url_for("admin_login")
        )

    connection = get_connection()
    cursor = connection.cursor()

    try:

    # =================================================
        # VOTERS
        # =================================================

        cursor.execute(
            """
            SELECT
                voter_id,
                full_name,
                email,
                voter_number,
                dob,
                aadhaar_number,
                pan_number,
                document_verified,
                status
            FROM voters
            ORDER BY voter_id DESC
            """
        )

        voters = cursor.fetchall()

        # =================================================
        # CANDIDATES
        # =================================================

        cursor.execute(
            """
            SELECT
                candidate_id,
                candidate_name,
                party_name,
                symbol
            FROM candidates
            ORDER BY candidate_id
            """
        )

        candidates_data = cursor.fetchall()

    finally:

        cursor.close()
        connection.close()

    return render_template(
        "admin_dashboard.html",
        voters=voters,
        candidates=candidates_data
    )


# =================================================
# APPROVE VOTER
# =================================================

@app.route(
    "/admin/approve/<int:voter_id>",
    methods=["POST"]
)
def approve_voter(voter_id):

    if "admin_id" not in session:

        return redirect(
            url_for("admin_login")
        )

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE voters
            SET status = 'Approved'
            WHERE voter_id = %s
            AND document_verified = TRUE
            """,
            (voter_id,)
        )

        connection.commit()

    finally:

        cursor.close()
        connection.close()

    flash(
        "Voter approved successfully.",
        "success"
    )

    return redirect(
        url_for("admin_dashboard")
    )


# =================================================
# REJECT VOTER
# =================================================

@app.route(
    "/admin/reject/<int:voter_id>",
    methods=["POST"]
)
def reject_voter(voter_id):

    if "admin_id" not in session:

        return redirect(
            url_for("admin_login")
        )

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE voters
            SET status = 'Rejected'
            WHERE voter_id = %s
            """,
            (voter_id,)
        )

        connection.commit()

    finally:

        cursor.close()
        connection.close()

    flash(
        "Voter rejected.",
        "warning"
    )

    return redirect(
        url_for("admin_dashboard")
    )


# =================================================
# ADD CANDIDATE
# =================================================

@app.route(
    "/admin/add_candidate",
    methods=["POST"]
)
def add_candidate():

    if "admin_id" not in session:

        return redirect(
            url_for("admin_login")
        )

    candidate_name = request.form.get("candidate_name")
    party_name = request.form.get("party_name")
    symbol = request.form.get("symbol")

    if not candidate_name or not party_name or not symbol:

        flash(
            "Please fill all candidate details.",
            "danger"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO candidates
            (
                candidate_name,
                party_name,
                symbol
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                candidate_name,
                party_name,
                symbol
            )
        )

        connection.commit()

        flash(
            "Candidate added successfully.",
            "success"
        )

    except Exception as error:

        connection.rollback()

        print("Candidate Error:", error)

        flash(
            "Candidate could not be added.",
            "danger"
        )

    finally:

        cursor.close()
        connection.close()

    return redirect(
        url_for("admin_dashboard")
    )


# =================================================
# DELETE CANDIDATE
# =================================================

@app.route(
    "/admin/delete_candidate/<int:candidate_id>",
    methods=["POST"]
)
def delete_candidate(candidate_id):

    if "admin_id" not in session:

        return redirect(
            url_for("admin_login")
        )

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM candidates
            WHERE candidate_id = %s
            """,
            (candidate_id,)
        )

        connection.commit()

        flash(
            "Candidate deleted successfully.",
            "success"
        )

    except Exception as error:

        connection.rollback()

        print("Delete Candidate Error:", error)

        flash(
            "Candidate could not be deleted.",
            "danger"
        )

    finally:

        cursor.close()
        connection.close()

    return redirect(
        url_for("admin_dashboard")
    )


# =================================================
# LOGOUT
# =================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("index")
    )


# =================================================
# RUN FLASK
# =================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
