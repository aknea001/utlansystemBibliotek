import qrcode

bokID = int(input("BokID: "))

img = qrcode.make(f"http://localhost:8080/{bokID}")

img.save("qrCode.png")