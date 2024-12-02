# Python libraries
import streamlit as st
import os
import hashlib
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# Local imports
# import the page title
from wofofiles.globfuncs import get_app_title
# import the menu
from wofofiles.menu import app_menu
# import the database connection
from wofofiles.conn import username, password, host, port, database

# page config
st.set_page_config(
    page_title=get_app_title(),
    layout='centered',
    initial_sidebar_state="collapsed"
)


# Create a connection string for the MySQL database
connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
engine = create_engine(connection_string, echo=True)


# Hashing the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
   

# Users CRUD
def users_page():
    st.subheader("Manage Users")
    
    # Add a new user
    st.write("### Add a New User")
    user_code = st.text_input("User Code")
    user_name = st.text_input("User Name")
    password = st.text_input("Password", type="password")

    if st.button("Add User"):
        if user_code and user_name and password:
            hashed_password = hash_password(password)
            try:
                with engine.begin() as connection:
                    insert_query = text("INSERT INTO users (UserCode, UserName, Password) VALUES (:user_code, :user_name, :password)")
                    connection.execute(insert_query, {'user_code': user_code, 'user_name': user_name, 'password': hashed_password})
                    st.success(f"User '{user_name}' added successfully!")
            except IntegrityError:
                st.error(f"Failed to add user: User code '{user_code}' already exists.")
            except SQLAlchemyError as e:
                st.error(f"Failed to add user: {str(e.__dict__['orig'])}")
        else:
                st.warning("Please enter all user details before adding.")

    # View, update, or delete a user
    st.write("### Existing Users")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT UserCode, UserName FROM users"))
            users = result.fetchall()
            if users:
                user_options = {f"{user.UserCode}: {user.UserName}": user.UserCode for user in users}
                selected_user = st.selectbox("Select a user to update or delete", list(user_options.keys()))
                selected_user_code = user_options[selected_user]
                
                st.divider()
                
                # Update the selected user
                st.write("### Update User")
                new_user_code = st.text_input("New User Code", value=str(selected_user_code))
                new_user_name = st.text_input("New User Name", value=selected_user.split(': ', 1)[1])
                new_password = st.text_input("New Password", type="password")
                
                if st.button("Update User"):
                    if new_user_name and new_user_code:
                        try:
                            with engine.begin() as connection:
                                update_query = text("UPDATE users SET UserCode = :new_user_code, UserName = :new_user_name" + (", Password = :new_password" if new_password else "") + " WHERE UserCode = :user_code")
                                params = {
                                    'new_user_code': new_user_code,
                                    'new_user_name': new_user_name,
                                    'user_code': selected_user_code
                                }
                                if new_password:
                                    params['new_password'] = hash_password(new_password)
                                connection.execute(update_query, params)
                                st.success(f"User '{selected_user_code}' updated successfully!")
                        except SQLAlchemyError as e:
                            st.error(f"Failed to update user: {str(e.__dict__['orig'])}")
                    else:
                        st.warning("Please enter all new user details before updating.")
                
                # Delete the selected user
                if st.button("Delete User"):
                    try:
                        with engine.begin() as connection:
                            delete_query = text("DELETE FROM users WHERE UserCode = :user_code")
                            result = connection.execute(delete_query, {'user_code': selected_user_code})
                            if result.rowcount > 0:
                                st.success(f"User with code '{selected_user_code}' deleted successfully!")
                            else:
                                st.warning(f"No user found with code '{selected_user_code}'.")
                    except SQLAlchemyError as e:
                        st.error(f"Failed to delete user: {str(e.__dict__['orig'])}")
            else:
                st.write("No users found.")
    except SQLAlchemyError as e:
        st.error(f"Failed to retrieve users: {str(e.__dict__['orig'])}")

# Groups CRUD
def groups_page():
    st.subheader("Manage Groups")

    # Add a new group
    st.write("### Add a New Group")
    group_code = st.text_input("Group Code")
    group_name = st.text_input("Group Name")

    if st.button("Add Group"):
        if group_code and group_name:
            try:
                with engine.begin() as connection:
                    insert_query = text("INSERT INTO `groups` (GroupCode, GroupName) VALUES (:group_code, :group_name)")
                    connection.execute(insert_query, {'group_code': group_code, 'group_name': group_name})
                    st.success(f"Group '{group_name}' added successfully!")
            except IntegrityError:
                st.error(f"Failed to add group: Group code '{group_code}' already exists.")
            except SQLAlchemyError as e:
                st.error(f"Failed to add group: {str(e.__dict__['orig'])}")
        else:
            st.warning("Please enter all group details before adding.")

    # View, update, or delete a group
    st.write("### Existing Groups")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT GroupCode, GroupName FROM `groups`"))
            groups = result.fetchall()
            if groups:
                group_options = {f"{group.GroupCode}: {group.GroupName}": group.GroupCode for group in groups}
                selected_group = st.selectbox("Select a group to update or delete", list(group_options.keys()))
                selected_group_code = group_options[selected_group]
                
                st.divider()
                
                # Update the selected group
                st.write("### Update Group")
                new_group_code = st.text_input("New Group Code", value=str(selected_group_code))
                new_group_name = st.text_input("New Group Name", value=selected_group.split(': ', 1)[1])
                
                if st.button("Update Group"):
                    if new_group_name and new_group_code:
                        try:
                            with engine.begin() as connection:
                                update_query = text("UPDATE `groups` SET GroupCode = :new_group_code, GroupName = :new_group_name WHERE GroupCode = :group_code")
                                connection.execute(update_query, {'new_group_code': new_group_code, 'new_group_name': new_group_name, 'group_code': selected_group_code})
                                st.success(f"Group '{selected_group_code}' updated successfully!")
                        except SQLAlchemyError as e:
                            st.error(f"Failed to update group: {str(e.__dict__['orig'])}")

                    else:
                        st.warning("Please enter all new group details before updating.")

                # Delete the selected group
                if st.button("Delete Group"):
                    try:
                        with engine.begin() as connection:
                            delete_query = text("DELETE FROM `groups` WHERE GroupCode = :group_code")
                            result = connection.execute(delete_query, {'group_code': selected_group_code})
                            if result.rowcount > 0:
                                st.success(f"Group with code '{selected_group_code}' deleted successfully!")
                            else:
                                st.warning(f"No group found with code '{selected_group_code}'.")
                    except SQLAlchemyError as e:
                        st.error(f"Failed to delete group: {str(e.__dict__['orig'])}")
            else:
                st.write("No groups found.")
    except SQLAlchemyError as e:
        st.error(f"Failed to retrieve groups: {str(e.__dict__['orig'])}")

# Sections CRUD
def sections_page():
    st.subheader("Manage Sections")

    # Add a new section
    st.write("### Add a New Section")
    section_code = st.text_input("Section Code")
    section_name = st.text_input("Section Name")

    if st.button("Add Section"):
        if section_code and section_name:
            try:
                with engine.begin() as connection:
                    insert_query = text("INSERT INTO sections (SectionCode, SectionName) VALUES (:section_code, :section_name)")
                    connection.execute(insert_query, {'section_code': section_code, 'section_name': section_name})
                    st.success(f"Section '{section_name}' added successfully!")
            except IntegrityError:
                st.error(f"Failed to add section: Section code '{section_code}' already exists.")
            except SQLAlchemyError as e:
                st.error(f"Failed to add section: {str(e.__dict__['orig'])}")
        else:
            st.warning("Please enter all section details before adding.")

    # View, update, or delete a section
    st.write("### Existing Sections")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT SectionCode, SectionName FROM sections"))
            sections = result.fetchall()
            if sections:
                section_options = {f"{section.SectionCode}: {section.SectionName}": section.SectionCode for section in sections}
                selected_section = st.selectbox("Select a section to update or delete", list(section_options.keys()))
                selected_section_code = section_options[selected_section]
                
                st.divider()
                
                # Update the selected section
                st.write("### Update Section")
                new_section_code = st.text_input("New Section Code", value=str(selected_section_code))
                new_section_name = st.text_input("New Section Name", value=selected_section.split(': ', 1)[1])
                
                if st.button("Update Section"):
                    if new_section_name and new_section_code:
                        try:
                            with engine.begin() as connection:
                                update_query = text("UPDATE sections SET SectionCode = :new_section_code, SectionName = :new_section_name WHERE SectionCode = :section_code")
                                connection.execute(update_query, {'new_section_code': new_section_code, 'new_section_name': new_section_name, 'section_code': selected_section_code})
                                st.success(f"Section '{selected_section_code}' updated successfully!")
                        except SQLAlchemyError as e:
                            st.error(f"Failed to update section: {str(e.__dict__['orig'])}")

                    else:
                        st.warning("Please enter all new section details before updating.")

                # Delete the selected section   
                if st.button("Delete Section"):
                    try:
                        with engine.begin() as connection:
                            delete_query = text("DELETE FROM sections WHERE SectionCode = :section_code")
                            result = connection.execute(delete_query, {'section_code': selected_section_code})
                            if result.rowcount > 0:
                                st.success(f"Section with code '{selected_section_code}' deleted successfully!")
                            else:
                                st.warning(f"No section found with code '{selected_section_code}'.")
                    except SQLAlchemyError as e:
                        st.error(f"Failed to delete section: {str(e.__dict__['orig'])}")
            else:
                st.write("No sections found.")
    except SQLAlchemyError as e:
        st.error(f"Failed to retrieve sections: {str(e.__dict__['orig'])}")

# Pages CRUD
def pages_page():
    st.subheader("Manage Pages")

    # Add a new page
    st.write("### Add a New Page")
    page_ref = st.text_input("Page Reference")
    page_name = st.text_input("Page Name")

    if st.button("Add Page"):
        if page_ref and page_name:
            try:
                with engine.begin() as connection:
                    insert_query = text("INSERT INTO pages (PageRef, PageName) VALUES (:page_ref, :page_name)")
                    connection.execute(insert_query, {'page_ref': page_ref, 'page_name': page_name})
                    st.success(f"Page '{page_name}' added successfully!")
            except IntegrityError:
                st.error(f"Failed to add page: Page reference '{page_ref}' already exists.")
            except SQLAlchemyError as e:
                st.error(f"Failed to add page: {str(e.__dict__['orig'])}")
        else:
            st.warning("Please enter all page details before adding.")

    # View, update, or delete a page
    st.write("### Existing Pages")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT PageRef, PageName FROM pages"))
            pages = result.fetchall()
            if pages:
                page_options = {f"{page.PageRef}: {page.PageName}": page.PageRef for page in pages}
                selected_page = st.selectbox("Select a page to update or delete", list(page_options.keys()))
                selected_page_ref = page_options[selected_page]
                
                st.divider()
                
                # Update the selected page
                st.write("### Update Page")
                new_page_ref = st.text_input("New Page Reference", value=str(selected_page_ref))
                new_page_name = st.text_input("New Page Name", value=selected_page.split(': ', 1)[1])
                
                if st.button("Update Page"):
                    if new_page_name and new_page_ref:
                        try:
                            with engine.begin() as connection:
                                update_query = text("UPDATE pages SET PageRef = :new_page_ref, PageName = :new_page_name WHERE PageRef = :page_ref")
                                connection.execute(update_query, {'new_page_ref': new_page_ref, 'new_page_name': new_page_name, 'page_ref': selected_page_ref})
                                st.success(f"Page '{selected_page_ref}' updated successfully!")
                        except SQLAlchemyError as e:
                            st.error(f"Failed to update page: {str(e.__dict__['orig'])}")

                    else:
                        st.warning("Please enter all new page details before updating.")

                # Delete the selected page
                if st.button("Delete Page"):
                    try:
                        with engine.begin() as connection:
                            delete_query = text("DELETE FROM pages WHERE PageRef = :page_ref")
                            result = connection.execute(delete_query, {'page_ref': selected_page_ref})
                            if result.rowcount > 0:
                                st.success(f"Page with reference '{selected_page_ref}' deleted successfully!")
                            else:
                                st.warning(f"No page found with reference '{selected_page_ref}'.")
                    except SQLAlchemyError as e:
                        st.error(f"Failed to delete page: {str(e.__dict__['orig'])}")
            else:
                st.write("No pages found.")
    except SQLAlchemyError as e:
        st.error(f"Failed to retrieve pages: {str(e.__dict__['orig'])}")

# Creating CRUD for the users access control
def access_control_page():
    st.subheader("Manage Access Control")

    # Load all options for dropdowns
    try:
        with engine.connect() as connection:
            users = connection.execute(text("SELECT UserCode, UserName FROM users")).fetchall()
            groups = connection.execute(text("SELECT GroupCode, GroupName FROM `groups`")).fetchall()
            sections = connection.execute(text("SELECT SectionCode, SectionName FROM sections")).fetchall()
            pages = connection.execute(text("SELECT PageRef, PageName FROM pages")).fetchall()

            # Create dictionaries for dropdowns
            user_options = {f"{user.UserName} ({user.UserCode})": user.UserCode for user in users}
            group_options = {"None": None} | {group.GroupName: group.GroupCode for group in groups}
            section_options = {"None": None} | {section.SectionName: section.SectionCode for section in sections}
            page_options = {page.PageName: page.PageRef for page in pages}

    except SQLAlchemyError as e:
        st.error(f"Failed to load options: {str(e.__dict__['orig'])}")
        return

    # Add a new access control entry
    st.write("### Add a New Access Control Entry")
    selected_user = st.selectbox("Select User", options=list(user_options.keys()))
    selected_group = st.selectbox("Select Group", options=list(group_options.keys()))
    selected_section = st.selectbox("Select Section", options=list(section_options.keys()))
    selected_page = st.selectbox("Select Page", options=list(page_options.keys()))

    if st.button("Add Access Control Entry"):
        if selected_user and selected_page:
            try:
                with engine.begin() as connection:
                    insert_query = text("""
                        INSERT INTO access_control (UserCode, GroupCode, SectionCode, PageRef) 
                        VALUES (:user_code, :group_code, :section_code, :page_ref)
                    """)
                    connection.execute(insert_query, {
                        'user_code': user_options[selected_user],
                        'group_code': group_options[selected_group],
                        'section_code': section_options[selected_section],
                        'page_ref': page_options[selected_page]
                    })
                    st.success("Access control entry added successfully!")
            except IntegrityError:
                st.error("Failed to add access control entry: Integrity error.")
            except SQLAlchemyError as e:
                st.error(f"Failed to add access control entry: {str(e.__dict__['orig'])}")
        else:
            st.warning("Please select all required details before adding.")

    # View, update, or delete an access control entry
    st.write("### Existing Access Control Entries")
    try:
        with engine.connect() as connection:
            query = text("""
                SELECT ac.UserCode, u.UserName, ac.GroupCode, g.GroupName, 
                       ac.SectionCode, s.SectionName, ac.PageRef, p.PageName
                FROM access_control ac
                JOIN users u ON ac.UserCode = u.UserCode
                LEFT JOIN `groups` g ON ac.GroupCode = g.GroupCode
                LEFT JOIN sections s ON ac.SectionCode = s.SectionCode
                LEFT JOIN pages p ON ac.PageRef = p.PageRef
            """)
            entries = connection.execute(query).fetchall()
            
            if entries:
                entry_display = [f"{entry.UserName} - {entry.GroupName or 'No Group'} - {entry.SectionName or 'No Section'} - {entry.PageName}" for entry in entries]
                selected_entry_idx = st.selectbox("Select an entry to update or delete", range(len(entry_display)), format_func=lambda x: entry_display[x])
                selected_entry = entries[selected_entry_idx]
                
                st.divider()
                
                # Update the selected entry
                st.write("### Update Access Control Entry")
                new_user = st.selectbox("New User", options=list(user_options.keys()), index=list(user_options.values()).index(selected_entry.UserCode))
                new_group = st.selectbox("New Group", options=list(group_options.keys()), 
                                       index=list(group_options.values()).index(selected_entry.GroupCode) if selected_entry.GroupCode in group_options.values() else 0)
                new_section = st.selectbox("New Section", options=list(section_options.keys()),
                                         index=list(section_options.values()).index(selected_entry.SectionCode) if selected_entry.SectionCode in section_options.values() else 0)
                new_page = st.selectbox("New Page", options=list(page_options.keys()),
                                      index=list(page_options.values()).index(selected_entry.PageRef))
                
                if st.button("Update Access Control Entry"):
                    try:
                        with engine.begin() as connection:
                            update_query = text("""
                                UPDATE access_control 
                                SET UserCode = :new_user_code, GroupCode = :new_group_code, 
                                    SectionCode = :new_section_code, PageRef = :new_page_ref 
                                WHERE UserCode = :old_user_code AND PageRef = :old_page_ref
                            """)
                            connection.execute(update_query, {
                                'new_user_code': user_options[new_user],
                                'new_group_code': group_options[new_group],
                                'new_section_code': section_options[new_section],
                                'new_page_ref': page_options[new_page],
                                'old_user_code': selected_entry.UserCode,
                                'old_page_ref': selected_entry.PageRef
                            })
                            st.success("Access control entry updated successfully!")
                    except SQLAlchemyError as e:
                        st.error(f"Failed to update access control entry: {str(e.__dict__['orig'])}")

                # Delete the selected entry
                if st.button("Delete Access Control Entry"):
                    try:
                        with engine.begin() as connection:
                            delete_query = text("DELETE FROM access_control WHERE UserCode = :user_code AND PageRef = :page_ref")
                            result = connection.execute(delete_query, {
                                'user_code': selected_entry.UserCode,
                                'page_ref': selected_entry.PageRef
                            })
                            if result.rowcount > 0:
                                st.success("Access control entry deleted successfully!")
                            else:
                                st.warning("No access control entry found.")
                    except SQLAlchemyError as e:
                        st.error(f"Failed to delete access control entry: {str(e.__dict__['orig'])}")
            else:
                st.write("No access control entries found.")
    except SQLAlchemyError as e:
        st.error(f"Failed to retrieve access control entries: {str(e.__dict__['orig'])}")

# Add the access control page to the MAC page
def mac_page():
    st.title("Meerkat Access Control")

    # Select page to manage
    page = st.selectbox("Select a page to manage", ("", "Manage Users", "Manage Groups", "Manage Sections", "Manage Pages", "Manage Permissions"))

    if page == "Manage Users":
        users_page()
    if page == "Manage Groups":
        groups_page()
    if page == "Manage Sections":
        sections_page()     
    if page == "Manage Pages":
        pages_page()       
    if page == "Manage Permissions":
        access_control_page()

# Display the MAC page if this script is run
def main():
    # Check if the user is logged in
    if st.session_state.get('logged_in'):
        try:
            with engine.connect() as connection:
                user_group_query = text("""
                    SELECT g.GroupName 
                    FROM users u
                    JOIN access_control ac ON u.UserCode = ac.UserCode
                    JOIN `groups` g ON ac.GroupCode = g.GroupCode
                    WHERE u.UserCode = :user_code
                """)
                result = connection.execute(user_group_query, {'user_code': st.session_state.get('user_code')}).fetchone()
                user_group = result.GroupName if result else None
                st.session_state['user_group'] = user_group
        except SQLAlchemyError as e:
            st.error(f"Failed to retrieve user group: {str(e.__dict__['orig'])}")
            return

        # Check user access to the MAC page if the group is admin
        if st.session_state.get('user_group') == 'Admin':
            mac_page()
        else:
            st.warning("You do not have permission to access this page.")

        # Sidebar with navigation options
        with st.sidebar:
            st.write(f"Welcome, {st.session_state['user_name']}!")
            # the main menu
            app_menu()
    else:
        st.warning("You must log in to access this page.")
        st.stop()  # Stops execution if not logged in

if __name__ == "__main__":
    main()