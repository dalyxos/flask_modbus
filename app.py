#! /usr/bin/env python3

from routes import app

def main():
    app.run(host='0.0.0.0', port=8000)

if __name__ == "__main__":
    main()