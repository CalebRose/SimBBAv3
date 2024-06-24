# Read the first few lines of the newly uploaded box score CSV file to inspect its structure
box_score_file_path = (
    "../simulation/BBA/cbs/Week 1/A/box_scores/1_Tennessee_Temple_box_score.csv"
)

with open(box_score_file_path, "r") as file:
    box_score_sample_lines = [next(file) for _ in range(10)]
    print(box_score_sample_lines)
