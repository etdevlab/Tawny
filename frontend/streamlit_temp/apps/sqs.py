#!/bin/bash/python3
import streamlit as st

import sys
import os
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    os.pardir,
    "backend")
)
sys.path.append(PROJECT_ROOT)

import modules.sqs as sqs

def app():
    st.title("SQS Stats")
    st.dataframe(sqs.get_attributes()["Attributes"])
    st.button("Refresh", on_click=print("Clicked"))
