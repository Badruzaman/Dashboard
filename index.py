
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL

import dash_bootstrap_components as dbc

from app import app
from flask_login import logout_user, current_user
from views import login, error, default, page2, profile, user_admin,role,role_menu
from apps.tissue.views import crm, topsale, productoverview, salesorderoverview
from config import conn_security


navBar = dbc.Navbar(id='navBar',
    children=[],
     sticky='top',
    color='primary',
    className='navbar navbar-expand-lg navbar-dark bg-primary',
)


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        navBar,
        html.Div(id='pageContent')
    ])
], id='table-wrapper')


################################################################################
# HANDLE PAGE ROUTING - IF USER NOT LOGGED IN, ALWAYS RETURN TO LOGIN SCREEN
################################################################################
@app.callback(Output('pageContent', 'children'),
              [Input('url', 'pathname')])
def displayPage(pathname):
    if pathname == '/':
        if current_user.is_authenticated:
            return default.layout
        else:
            return login.layout

    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            return login.layout
        else:
            return login.layout

    if pathname.lower() == '/page1':
        if current_user.is_authenticated:
            return default.layout
        else:
            return login.layout
        
    if pathname.lower() == '/page3':
        if current_user.is_authenticated:
            return crm.crm_dash
        else:
            return login.layout
    if pathname == '/page2':
        if current_user.is_authenticated:
            return crm.crm_dash
        else:
            return login.layout

    if pathname == '/role':
        if current_user.is_authenticated:
            return role.layout
        else:
            return login.layout

    if pathname == '/role_menu':
        if current_user.is_authenticated:
            return role_menu.layout
        else:
            return login.layout

    if pathname == '/productoverview':
        if current_user.is_authenticated:
            return productoverview.layout
        else:
            return login.layout

    if pathname == '/salesorderoverview':
        if current_user.is_authenticated:
            return salesorderoverview.layout
        else:
            return login.layout

    if pathname == '/profile':
        if current_user.is_authenticated:
            return profile.layout
        else:
            return login.layout

    if pathname == '/admin':
        if current_user.is_authenticated:
            if current_user.admin == 1:
                return user_admin.layout
            else:
                return error.layout
        else:
            return login.layout


    else:
        return error.layout


################################################################################
@app.callback(
    Output('navBar', 'children'),
    [Input('pageContent', 'children')])
def navBar(input1):
    if current_user.is_authenticated:
        if current_user.admin == 1:

            child_tissue = []
            child_Config = []
            tisse_menu = ''
            config_menu = ''

            user_id = current_user.id
            cursor = conn_security.cursor()
            stored_proc = f"exec spGetUserMenu @Id = {user_id}"
            cursor.execute(stored_proc)
            result = cursor.fetchall()
            user_menus = list(result)


            for item in user_menus:
                if item[6] == 'Config':
                    appended_item = dbc.DropdownMenuItem('{}'.format(item[7]), href='{}'.format(item[8]))
                    child_Config.append(appended_item)
                elif item[6] == 'Tissue':
                    appended_item = dbc.DropdownMenuItem('{}'.format(item[7]), href='{}'.format(item[8]))
                    child_tissue.append(appended_item)
                else:
                    pass

            if len(child_tissue) > 0:
                tisse_menu = dbc.DropdownMenu(
                            nav=True,
                            in_navbar=True,
                            label="Tissue",
                            children=child_tissue
                        )
            if len(child_Config) > 0:
                config_menu = dbc.DropdownMenu(
                            nav=True,
                            in_navbar=True,
                            label="Configuration",
                            children=child_Config
                        )
            navBarContents = [
                     tisse_menu,
                     config_menu,
                     # menu_list,
                    dbc.DropdownMenu(
                        nav=True,
                        in_navbar=True,
                        label=current_user.username,
                        children=[
                            dbc.DropdownMenuItem('Profile', href='/profile'),
                            dbc.DropdownMenuItem('Admin', href='/admin'),
                            dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem('Logout', href='/logout'),
                        ],
                    ),
                ]
            return navBarContents

        else:

            child_tissue = []
            child_Config = []
            tisse_menu = ''
            config_menu = ''

            user_id = current_user.id
            cursor = conn_security.cursor()
            stored_proc = f"exec spGetUserMenu @Id = {user_id}"

            cursor.execute(stored_proc)
            result = cursor.fetchall()
            user_menus = list(result)

            for item in user_menus:
                if item[6] == 'Config':
                    appended_item = dbc.DropdownMenuItem('{}'.format(item[7]), href='{}'.format(item[8]))
                    child_Config.append(appended_item)
                elif item[6] == 'Tissue':
                    appended_item = dbc.DropdownMenuItem('{}'.format(item[7]), href='{}'.format(item[8]))
                    child_tissue.append(appended_item)
                else:
                    pass

            if len(child_tissue) > 0:
                tisse_menu = dbc.DropdownMenu(
                    nav=True,
                    in_navbar=True,
                    label="Tissue",
                    children=child_tissue
                )
            if len(child_Config) > 0:
                config_menu = dbc.DropdownMenu(
                    nav=True,
                    in_navbar=True,
                    label="Configuration",
                    children=child_Config
                )
            navBarContents = [
                    tisse_menu,
                    config_menu,
                    dbc.DropdownMenu(
                        nav=True,
                        in_navbar=True,
                        label=current_user.username,
                        children=[
                            dbc.DropdownMenuItem('Profile', href='/profile'),
                            dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem('Logout', href='/logout'),
                        ],
                    ),
                ]
            # navBarContents = [
            #     # dbc.NavItem(dbc.NavLink('Page 1', href='/page1')),
            #     # dbc.NavItem(dbc.NavLink('Page 2', href='/page2')),
            #     dbc.DropdownMenu(
            #         nav=True,
            #         in_navbar=True,
            #         label='BAPL',
            #         children=[
            #             dbc.DropdownMenuItem('Top Sales', href='/page1'),
            #             # dbc.DropdownMenuItem('Admin', href='/admin'),
            #             # dbc.DropdownMenuItem(divider=True),
            #             # dbc.DropdownMenuItem('Logout', href='/logout'),
            #         ],
            #     ),
            #     dbc.DropdownMenu(
            #         nav=True,
            #         in_navbar=True,
            #         label='Tissue',
            #         children=[
            #             dbc.DropdownMenuItem('Category Wise Sales', href='/page2'),
            #             # dbc.DropdownMenuItem('Admin', href='/admin'),
            #             # dbc.DropdownMenuItem(divider=True),
            #             # dbc.DropdownMenuItem('Logout', href='/logout'),
            #         ],
            #     ),
            #     dbc.DropdownMenu(
            #         nav=True,
            #         in_navbar=True,
            #         label=current_user.username,
            #         children=[
            #             dbc.DropdownMenuItem('Profile', href='/profile'),
            #             dbc.DropdownMenuItem(divider=True),
            #             dbc.DropdownMenuItem('Logout', href='/logout'),
            #         ],
            #     ),
            # ]
            return navBarContents

    else:
        return ''



if __name__ == '__main__':
    app.run_server(debug=True,port=3000)