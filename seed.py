seed.py
from db import init, connect

# Fictional sample profile for demonstration purposes.
# Replace these values with your own verified information.
# Do not commit real personal information to a public repository.

SAMPLE_FACTS = [
    ("personal", "Full Name", "Alex Morgan"),
    ("personal", "Email", "alex.morgan@example.com"),
    ("personal", "Location", "Minneapolis, MN"),

    ("education", "University", "Example State University"),
    ("education", "Degree", "Bachelor of Science in Computer Science"),
    ("education", "Graduation", "May 2027"),

    ("skills", "Programming", "Python, Java, JavaScript, SQL"),
    ("skills", "Frameworks", "React, Flask, Spring Boot"),
    ("skills", "Databases", "PostgreSQL, SQLite"),
    ("skills", "Tools", "Git, GitHub, Docker, REST APIs"),

    ("experience", "Software Development Intern",
     "Developed REST API endpoints and collaborated with a team "
     "to build internal web application features."),

    ("projects", "Task Management Application",
     "Built a task management application using React, Flask, "
     "and SQLite with CRUD operations and a responsive interface."),

    ("projects", "Weather Dashboard",
     "Developed a Python application that retrieves weather data "
     "from a public API and displays current conditions."),

    ("preferences", "Target Roles",
     "Entry-level Software Engineer, Backend Developer, Software Developer"),
    ("preferences", "Preferred Locations",
     "Remote United States, Minneapolis, MN"),
    ("preferences", "Work Authorization",
     "Not specified. Verify eligibility with the candidate."),
    ("preferences", "Sponsorship",
     "Not specified. Verify sponsorship requirements with the candidate."),
]


def main():
    init()

    with connect() as con:
        existing = con.execute("SELECT COUNT(*) FROM facts").fetchone()[0]

        if existing > 0:
            print("Profile already contains data. No sample facts were added.")
            return

        con.executemany(
            """
            INSERT INTO facts (category, label, value, status)
            VALUES (?, ?, ?, 'verified')
            """,
            SAMPLE_FACTS,
        )

    print("Fictional sample profile added successfully.")


if __name__ == "__main__":
    main()