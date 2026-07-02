#!/usr/bin/env python3
import os
os.environ["APP_ENV"] = "production"

import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=4)
