import socket
import select
import sys

def monitoring(connections: list)-> None:

    should_listen = True
    active_sockets = [info['Socket'] for info in connections]
    prompt_displayed = False

    while should_listen:
        try:
            read_sockets, _, _ = select.select(active_sockets + [sys.stdin], [], [], .1)
            # Print the default message prompt
            if not prompt_displayed:
                sys.stdout.write(">> ")
                sys.stdout.flush()  # Flush to ensure the message is immediately displayed
                prompt_displayed = True

            for sock in read_sockets:
                user_input = ''
                if sock == sys.stdin:
                    # print('IN')
                   user_input = sys.stdin.readline().strip()
                   prompt_displayed = False
                   if user_input:
                        for bridge in active_sockets:
                            bridge.send(user_input.encode())
                   
                
                else:
                    data = sock.recv(1024)
                    print(data)
                    if data:
                        if len(data) < 12:
                            print("Incomplete frame received, discarding.")
                            continue
        
        except socket.error as e:
            print(f"Socket error: {e}")

        except select.error as e:
            print(f"Select error: {e}")

        except KeyError as e:
            print(f"Key error: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")
                