import subprocess
import re

def run_drakul(radius, mode):
    process = subprocess.Popen(
        [r"C:\Users\Hind\AppData\Local\Programs\Python\Python310\python.exe",
         r"C:\Users\Hind\Downloads\nocturna.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # send YOUR chosen values
    inputs = f"{radius}\n{mode}\n"
    output, error = process.communicate(inputs)

    score_match = re.search(r"SCORE:\s*(\d+)", output)
    link_match = re.search(r"https://www.google.com/maps\?q=[^\s]+", output)

    score = int(score_match.group(1)) if score_match else None
    link = link_match.group(0) if link_match else None

    return {
        "score": score,
        "link": link,
        "raw": output
    }


# 🔥 manual test (you choose here)
if __name__ == "__main__":
    radius = int(input("Radius: "))
    mode = input("Mode: ")

    result = run_drakul(radius, mode)
    print(result)