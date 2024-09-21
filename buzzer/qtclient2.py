import socket
import os
import time
import cv2
import numpy as np

DEVICE_FILENAME = '/dev/buzzer_dev'
SERVER_IP = '10.10.141.48'
SERVER_PORT = 5000

def connect_to_server():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        return client_socket
    except Exception as e:
        print(f"서버 연결 실패 : {e}")
        return None

def main():
    client_socket = connect_to_server()

    if client_socket:
        try:
            # 부저 장치 파일 열기
            try:
                device = os.open(DEVICE_FILENAME, os.O_WRONLY)
            except OSError as e:
                print(f"Failed to open device: {e}")
                client_socket.close()
                return

            # 웹캠 설정
            cap = cv2.VideoCapture(1)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

            while True:
                # 서버로부터 메시지 읽기
                try:
                    buffer = client_socket.recv(1024).decode('utf-8').strip()
                    
                    # "buzzer_on" 메시지 확인
                    if buffer == "buzzer_on":
                        buzzer_on = b'\x01'
                        os.write(device, buzzer_on)
                        print("Turning on buzzer...")
                        # time.sleep(2)  # 부저를 2초 동안 울리기

                    elif buffer == "buzzer_off":
                        buzzer_off = b'\x00'
                        os.write(device, buzzer_off)
                        print("Turning off buzzer...")

                    # 웹캠에서 프레임 읽기
                    ret, frame = cap.read()
                    if not ret:
                        print("웹캠에서 프레임을 읽지 못했습니다.")
                        break

                    # 이미지를 JPEG 형식으로 인코딩
                    result, frame = cv2.imencode('.jpg', frame, encode_param)
                    data = np.array(frame)
                    byteData = data.tobytes()

                    # 데이터 크기와 데이터를 전송
                    client_socket.sendall((str(len(byteData))).encode().ljust(16) + byteData)
                
                except BrokenPipeError:
                    print("[Error] 서버와 연결이 끊어졌습니다. 연결을 재시도합니다.")
                    client_socket.close()
                    client_socket = connect_to_server()
                    if not client_socket:
                        break
                except Exception as e:
                    print(f"[연결 종료] {e}")
                    break

        finally:
            if client_socket is not None:
                client_socket.close()
            if 'device' in locals():
                os.close(device)
            cap.release()
    else:
        print("서버에 연결할 수 없어 프로그램을 종료합니다.")

if __name__ == '__main__':
    main()

