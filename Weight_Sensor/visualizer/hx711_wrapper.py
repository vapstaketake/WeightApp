import subprocess

class HX711:
    def get_raw_reading(EXECUTABLE_PATH):
        """
        センサーからの生の読み取り値を取得するメソッド。
        """
        try:
            result=subprocess.run([EXECUTABLE_PATH], capture_output=True, text=True, check=True)
            if result.returncode == 0:
                return float(result.stdout.decode().strip())
            else:
                print("Error:", result.stderr.decode())
        except Exception as e:
            print("Error:", e)
        return None
