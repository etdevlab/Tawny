import streamlit as st
from streamlit_agraph import agraph, TripleStore, Node, Edge, Config

import sys
import os
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    os.pardir,
    "backend")
)

import modules.arangodb as database

def getGraphData():
    db = database.getDatabase()

    aql = """
    LET programs = (
    FOR program IN Programs
        RETURN {
            "id": program._id,
            "label": program.handle,
            "image": program.profile_picture
        }
    )
    LET scopes = (
        FOR program IN Programs
            FOR v,e,p IN 1..1 OUTBOUND program ProgramScopeLinks
                RETURN{
                    "id": v._id,
                    "label": v.asset_identifier
                }
    )
    LET edges = (
        FOR program IN Programs
            FOR v,e,p IN 1..1 OUTBOUND program ProgramScopeLinks
                RETURN{
                    "source": program._id,
                    "target": v._id,
                    "label": v.asset_type
                }
    ) 
    RETURN{
        programs: programs,
        scopes: scopes,
        edges: edges
    } 
    """

    results = db.AQLQuery(aql, rawResults=True)
    results = list(results)

    for result in results:
        for program in result["programs"]:
            node = {
                "id": program["id"],
                "label": program["label"],
                "size": 25,
                "shape": "circularImage",
                "image": program["image"],
                "full": program
            }

            if node not in st.session_state.nodes:
                st.session_state.nodes.append(node)
        #for scope in result["scopes"]:
        #    nodes.append( Node(
        #                id=scope["id"],
        #                size=10,
        #                shape="dot",
        #                label=program["label"])
        #            )
        #for edge in result["edges"]:
        #    edges.append( Edge(
        #                source=edge["source"],
        #                target=edge["target"],
        #                label=edge["label"])
        #    )

    return

def loadEdges(document):

    col1 = document.split("/")[0]
    if col1 == "Programs":
        aql = """
        LET doc = DOCUMENT(@doc)
        FOR v,e,p IN 1..1 OUTBOUND doc ProgramScopeLinks
            RETURN{
                node: {
                    id: v._id,
                    label: v.asset_identifier
                },
                edge: {
                    source: doc._id,
                    target: v._id,
                    label: v.asset_type
                }   
            } 
        """

        results = database.getDatabase().AQLQuery(aql, rawResults=True, bindVars={"doc": document})
        results = list(results)

        for result in results:
            node = {
                "id": result["node"]["id"],
                "label": result["node"]["label"],
                "size": 10,
                "shape": "dot"
            }
            if node not in st.session_state.nodes:
                st.session_state.nodes.append(node)
            
            edge = {
                "source": result["edge"]["source"],
                "target": result["edge"]["target"],
                "label": result["edge"]["label"]
            }
            if edge not in st.session_state.edges:
                st.session_state.edges.append(edge)

    else:
        return

    return

def addProgram(program):
    db = database.getDatabase()

    aql = """
    RETURN Document(@doc)
    """

    results = db.AQLQuery(aql, rawResults=True, bindVars={'doc': "Programs/"+str(program)})
    results = list(results)
    for result in results:
        if not result: continue
        node = {
            "id": result["_id"],
            "label": result["handle"],
            "size": 25,
            "shape": "circularImage",
            "image": result["profile_picture"],
            "full": result
        }

        if node not in st.session_state.nodes:
            st.session_state.nodes.append(node)


###MAIN
def app():
    global return_value
    st.title("Graph Test")
    st.text("Testing agraph stuff")

    ### INIT SESSION VARS
    if 'nodes' not in st.session_state:
        st.session_state['nodes'] = []
    if 'edges' not in st.session_state:
        st.session_state['edges'] = []

    st.write("Nodes")
    st.dataframe(st.session_state['nodes'])
    st.write("Edges")
    st.dataframe(st.session_state['edges'])

    #Load program nodes first
    programIdVal = st.number_input("Load Program Node by Key:", step=1)
    print(programIdVal)
    
    col1, col2 = st.columns([1,1])
    with col1:
        st.button('load', on_click=addProgram(programIdVal))
    with col2:
        st.button('load_all')
   
   


    config = Config(height=500, width=800, directed=True, hierarchial=True, collapsible=True)
    return_value = agraph(list([Node(**i) for i in st.session_state.nodes]), ([Edge(**i) for i in st.session_state.edges]), config)
    print(return_value)

    #TODO figure out da flow
    if return_value:
        st.header(return_value)
        st.dataframe(database.getDocument(return_value))

        action = st.selectbox(
            "Action",
            ("None", "Load Edges", "Scans"))

        if action == "Load Edges":
            loadEdges(return_value)
