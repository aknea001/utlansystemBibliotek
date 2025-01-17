def makeQR(bokID):
    import qrcode

    img = qrcode.make(f"http://localhost:8080/{bokID}")

    img.save("qrCode.png")