using System;
using System.Collections.Generic;
using System.Linq;
using System.Web.UI;
using CarpetRadar.Services.DataStorage;
using CarpetRadar.Services.Models;
using NLog;

namespace CarpetRadar.Web
{
    public partial class _Default : Page
    {
        protected List<CurrentPosition> flights;

        private readonly IDataStorage dataStorage;
        private readonly ILogger logger;

        public _Default(IDataStorage dataStorage, ILogger logger)
        {
            this.dataStorage = dataStorage;
            this.logger = logger;
        }

        protected void Page_Load(object sender, EventArgs e)
        {
            flights = dataStorage.GetCurrentPositions().GetAwaiter().GetResult().ToList();
            var users = dataStorage.GetUserInfos();
        }
    }
}
