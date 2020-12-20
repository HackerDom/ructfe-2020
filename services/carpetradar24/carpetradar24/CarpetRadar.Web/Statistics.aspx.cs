using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using CarpetRadar.Services.DataStorage;
using CarpetRadar.Services.IdentityServices;
using CarpetRadar.Services.Models;
using NLog;

namespace CarpetRadar.Web
{
    public partial class Statistics : Page
    {
        protected (string Login, string Company) userInfo;
        protected IEnumerable<Flight> userFlights;

        private readonly IAuthenticationService authenticationService;
        private readonly IDataStorage dataStorage;
        private readonly ILogger logger;

        public Statistics(IAuthenticationService authenticationService, IDataStorage dataStorage, ILogger logger)
        {
            this.authenticationService = authenticationService;
            this.dataStorage = dataStorage;
            this.logger = logger;
        }

        protected void Page_Load(object sender, EventArgs e)
        {
            var userId = authenticationService.ResolveUser(Request.Cookies["token"]).GetAwaiter().GetResult();
            if (userId == null)
            {
                Response.Redirect("/Login.aspx?ReturnUrl=Statistics.aspx", true);
                return;
            }

            userInfo = dataStorage.GetUserInfo(userId.Value).GetAwaiter().GetResult();
            userFlights = dataStorage.GetUserFlights(userId.Value).GetAwaiter().GetResult().ToList();
        }
    }
}
