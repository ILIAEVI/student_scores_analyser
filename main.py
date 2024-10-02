import pandas as pd
import matplotlib.pyplot as plt


def load_data(file_path):
    return pd.read_csv(file_path)


# 1. Students who did not pass any subject (less than 50 in any subject)
def get_failed_students(df):
    failed_students = df[df[['Math', 'Physics', 'Chemistry', 'Biology', 'English']].lt(50.0).any(axis=1)]
    return failed_students['Student'].unique()


# 2. Calculate average grade for each subject per semester
def get_average_grades_by_semester(df):
    average_grades_by_semester = df.groupby('Semester')[
        ['Math', 'Physics', 'Chemistry', 'Biology', 'English']].mean().reset_index()
    average_grades_by_semester.to_csv('average_grades_by_semester.csv', index_label='Index')
    return average_grades_by_semester


# 3. Find the student(s) with the highest overall average grade across all subjects and semesters
def get_highest_avg_grade_student(df):
    avg_grades_by_students = df.groupby('Student').mean(numeric_only=True)
    avg_grades_by_students['Overall Average'] = avg_grades_by_students.mean(axis=1)
    highest_avg_grade_student = avg_grades_by_students[
        avg_grades_by_students['Overall Average'] == avg_grades_by_students['Overall Average'].max()]
    return highest_avg_grade_student


# 4. Find the subject with the lowest average score across all semesters
def get_hardest_subject(df):
    df_melted = df.melt(id_vars=['Student', 'Semester'], var_name='Subject', value_name='Grade')
    df_melted = df_melted.dropna(subset=['Grade'])
    average_scores = df_melted.groupby('Subject')['Grade'].mean()
    hardest_subject = average_scores.idxmin()
    hardest_score = average_scores.min()
    return hardest_subject, hardest_score

# 5. Get students who consistently improved their grades
def get_improving_students(df):
    df_melted = df.melt(id_vars=['Student', 'Semester'], var_name='Subject', value_name='Grade')
    df_melted['Grade'] = pd.to_numeric(df_melted['Grade'], errors='coerce')

    df_avg = df_melted.groupby(['Student', 'Semester'])['Grade'].mean().reset_index()
    df_avg['Semester_Number'] = df_avg['Semester'].str.extract(r'(\d+)').astype(int)
    df_avg = df_avg.sort_values(by=['Student', 'Semester_Number'])

    students_with_multiple_semesters = df_avg.groupby('Student').filter(lambda x: len(x) >= 2)
    improving_students_data = []

    for student, group in students_with_multiple_semesters.groupby('Student'):
        if (group['Grade'].diff().dropna() > 0).all() and not group['Grade'].isnull().any():
            improving_students_data.append(group)

    improving_students_df = pd.concat(improving_students_data).reset_index(drop=True)
    improving_students_df = improving_students_df.drop(columns=['Semester_Number'])
    improving_students_df = improving_students_df.sort_values(by=['Student', 'Grade'])

    return improving_students_df

# 6. Create a bar chart for average scores across subjects
def plot_average_scores(df):
    df_melted = df.melt(id_vars=['Student', 'Semester'], var_name='Subject', value_name='Grade')

    subject_means = df_melted.groupby('Subject')['Grade'].mean()

    plt.figure(figsize=(8, 6))
    subject_means.plot(kind='bar', color='skyblue')
    plt.title('Average Score per Subject Across All Semesters')
    plt.xlabel('Subject')
    plt.ylabel('Average Score')
    plt.ylim(0, 100)
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig('average_score_per_subject.png')
    plt.show()

# 7. Create a line graph for average overall score by semester
def plot_average_overall_score_by_semester(df):
    df['Overall Average'] = df[['Math', 'Physics', 'Chemistry', 'Biology', 'English']].mean(axis=1)
    avg_overall_by_semester = df.groupby('Semester')['Overall Average'].mean().reset_index()

    plt.figure(figsize=(8, 6))
    plt.plot(avg_overall_by_semester['Semester'], avg_overall_by_semester['Overall Average'], marker='o', color='b', linestyle='-')
    plt.title('Average Overall Score by Semester')
    plt.xlabel('Semester')
    plt.ylabel('Average Overall Score')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig('average_overall_score_by_semester.png')
    plt.show()

def main(file_path):
    df = load_data(file_path)

    # 1. Get the students who failed any subject
    print("Failed Student List (first 10 Student): ")
    failed_students_list = get_failed_students(df)
    print(failed_students_list[0:10], end='\n\n')

    # 2. Calculate the average grades by semester
    avg_grades_by_semester = get_average_grades_by_semester(df)
    print("Average grades by semester:")
    print(avg_grades_by_semester, end='\n\n')

    # 3. Find the student with the highest overall average grade
    highest_avg_grade_student = get_highest_avg_grade_student(df)
    print("Student(s) with the highest average grade:")
    print(highest_avg_grade_student, end='\n\n')

    # 4. Find the subject in which students had the lowest average score
    hardest_subject, hardest_score = get_hardest_subject(df)
    print(
        f"The hardest subject to pass across all semesters is '{hardest_subject}' with an average score of {hardest_score:.2f}.\n", )

    # 5. Get students who consistently improved their grades
    improving_students_df = get_improving_students(df)
    print("DataFrame of students with consistently improved average grades sorted by Student and Grade:")
    print(improving_students_df, end='\n\n')

    # 6. Plot average scores across subjects
    plot_average_scores(df)

    # 7. Plot average overall score by semester
    plot_average_overall_score_by_semester(df)

if __name__ == "__main__":
    main('student_scores_random_names.csv')
