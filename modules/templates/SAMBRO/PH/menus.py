# -*- coding: utf-8 -*-

from gluon import *
from s3 import *
from s3layouts import *
try:
    from .layouts import *
except ImportError:
    pass
import s3menus as default

# =============================================================================
class S3MainMenu(default.S3MainMenu):
    """
        Custom Application Main Menu:

        The main menu consists of several sub-menus, each of which can
        be customised separately as a method of this class. The overall
        composition of the menu is defined in the menu() method, which can
        be customised as well:

        Function        Sub-Menu                Access to (standard)

        menu_modules()  the modules menu        the Eden modules
        menu_gis()      the GIS menu            GIS configurations
        menu_admin()    the Admin menu          System/User Administration
        menu_lang()     the Language menu       Selection of the GUI locale
        menu_auth()     the User menu           Login, Logout, User Profile
        menu_help()     the Help menu           Contact page, About page

        The standard uses the MM layout class for main menu items - but you
        can of course use a custom layout class which you define in layouts.py.

        Additional sub-menus can simply be defined as additional functions in
        this class, and then be included in the menu() method.

        Each sub-menu function returns a list of menu items, only the menu()
        function must return a layout class instance.
    """

    # -------------------------------------------------------------------------
    @classmethod
    def menu(cls):
        """ Compose Menu """

        main_menu = MM()(

            cls.menu_modules(),
            cls.menu_lang(right=True),
            cls.menu_auth(),
            cls.menu_admin(),
        )

        return main_menu

    # -------------------------------------------------------------------------
    @classmethod
    def menu_modules(cls):
        """ Custom Modules Menu """

        auth = current.auth
        has_role = auth.s3_has_role
        if auth.s3_logged_in():
            alerting_menu = MM("Alerting", c="cap", f="alert")
            mapping_menu = MM("Mapping", c="gis", f="index")
            recipient_menu = MM("Manage Recipients", c="pr", f="subscription",
                                vars={"option": "manage_recipient"})
            alert_hub_menu = MM("Alert Hub", c="cap", f="alert",
                                vars={"~.external": True})
            if has_role("ADMIN"):
                # Full set
                # @ToDo: Add menu entries for "Create RSS Feed for CAP" & "Create RSS Feed for CMS"
                return [homepage(args="alert_hub_cop"),
                        alerting_menu,
                        alert_hub_menu,
                        mapping_menu,
                        recipient_menu,
                        MM("Persons", c="pr", f="person"),
                        MM("Organizations", c="org", f="organisation"),
                        MM("Event Types", c="event", f="event_type"),
                        ]
            else:
                view_menu = [MM("View Alerts", c="cap", f="alert"),
                             alert_hub_menu,
                             ]
                # Publisher sees minimal options
                menus_ = [homepage(args="alert_hub_cop"),
                          ]

                if has_role("MAP_ADMIN"):
                    menus_.extend([view_menu,
                                   alert_hub_menu,
                                   mapping_menu,
                                  ])
                elif has_role("ALERT_APPROVER"):
                    menus_.extend([alerting_menu,
                                   alert_hub_menu,
                                   MM("Approve Alerts", c="cap", f="alert", m="review"),
                                   MM("View Approved Alerts", c="cap", f="alert",
                                      vars={"~.approved_by__ne": None}
                                      ),
                                   MM("Incomplete Alerts", c="cap", f="alert", m="review",
                                      vars={"status": "incomplete"}
                                      )
                                   ])
                elif has_role("ALERT_EDITOR"):
                    menus_.extend([alerting_menu,
                                   alert_hub_menu])
                else:
                    # Authenticated Users
                    menus_.append(view_menu)

                return menus_

        # Public or CUG reader sees minimal options
        return [homepage(args="alert_hub_cop"),
                ]

    # -------------------------------------------------------------------------
    @classmethod
    def menu_auth(cls, **attr):
        """ Auth Menu """

        auth = current.auth

        if not auth.is_logged_in():
            menu_auth = MM("Login", link=False, right=True)(
                           MM("Login", c="default", f="user", m="login",
                              vars={"_next": URL(c="cap", f="alert")}),
                           MM("Lost Password", c="default", f="user",
                              m="retrieve_password"),
                           MM("Request for Account", c="default", f="user",
                              m="register"),
                        )
        else:
            # Logged-in
            user_id = auth.s3_logged_in_person()                
            menu_auth = MM(auth.user.email, link=False, right=True)(
                           MM("Subscription", c="pr", f="subscription"),
                           MM("Edit Profile", c="pr", f="person", args=[user_id]),
                           MM("Change Password", c="default", f="user",
                              m="change_password"),
                           MM("Logout", c="default", f="user", m="logout"),
                        )

        return menu_auth

    # -------------------------------------------------------------------------
    @classmethod
    def menu_admin(cls, **attr):
        """ Administrator Menu """

        if current.auth.s3_has_role("ADMIN"):
            name_nice = current.deployment_settings.modules["admin"].name_nice
            menu_admin = MM(name_nice, c="admin", right=True, **attr)(
                            MM("Settings", f="setting"),
                            MM("Manage Users", f="user"),
                            MM("Database", c="appadmin", f="index"),
                            MM("Error Tickets", f="errors"),
                            #MM("Synchronization", c="sync", f="index"),
                         )
        else:
            menu_admin = None

        return menu_admin

# END =========================================================================