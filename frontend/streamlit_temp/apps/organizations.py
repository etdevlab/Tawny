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

import modules.arangodb as database

def app():
    st.title("Organizations")
    st.text("H1 Programs for now")

    @st.cache_resource(ttl=600)
    def getOrganizationData():
        db = database.getDatabase()

        aql = """
        FOR program IN Programs
            SORT TO_NUMBER(program._key) ASC
            RETURN {
                ProgramID: program._key,
                Name: program.name,
                Handle: program.handle,
                
                Bookmarked: program.bookmarked,
                BountySplitting: program.allows_bounty_splitting,
                HasBounties: program.offers_bounties,
                isPrivate: program.isPrivate,
                isActive: program.isActive,
                
                Submission_State: program.submission_state,
                Trage: program.triage_active,
                
                Started: program.started_accepting_at,
                Joined: program.last_invitation_accepted_at_for_user,
                firstAdded: program.firstAdded,
                lastActive: program.lastActive,

                Reports: program.number_of_reports_for_user,
                ValidReports: program.number_of_valid_reports_for_user,
                BountiesEarned: program.bounty_earned_for_user,

                Currency: program.currency,
                Type: program.type
            }
        """

        results = db.AQLQuery(aql, rawResults=True)
        return list(results)

    organizationData = getOrganizationData()
    st.dataframe(organizationData)
