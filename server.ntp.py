# extremely simply sntp server - just for network devices debug purposes

import sys, socket, logging, datetime, time, select, binascii

try:
    import ntplib
except ImportError:
    print("Required <ntplib>. Please install it with `pip install ntplib`.")
    sys.exit(2)

logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(message)s", datefmt="%d %b %X")
logger = logging.getLogger()


def run(ip, port=123):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(0)
    sock.bind((ip, port))
    logger.info(f"NTP Server started on {ip}:{port}. Press Ctrl+C for stop")

    while True:
        ready, _, _ = select.select([sock], [], [], 0.1)
        if ready:
            data, addr = sock.recvfrom(0x400)
            packet = ntplib.NTPPacket()
            packet.from_data(data)
            logger.info(f"IN ({addr}) {binascii.b2a_hex(data).decode()}")
            packet.mode = 4
            packet.stratum = 2
            packet.tx_timestamp = ntplib.system_to_ntp_time(time.time())
            sock.sendto(packet.to_data(), addr)
            logger.info(f"OUT({addr}) {binascii.b2a_hex(packet.to_data()).decode()}")


if __name__ == "__main__":
    try:
        ip = sys.argv[1] if len(sys.argv) > 1 else socket.gethostbyname_ex(socket.gethostname())[2][0]
        run(ip)  # use first ip address or type ip in command line
    except KeyboardInterrupt:
        logger.info("Ctrl+C")
