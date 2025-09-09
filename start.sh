#!/bin/bash
python3 backend/main.py &
cd frontend
npm run dev &
cd .. 