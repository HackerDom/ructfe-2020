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
        protected List<(CurrentPosition Position, string Login, string Company)> positionsData;

        private readonly IDataStorage dataStorage;
        private readonly ILogger logger;

        public _Default(IDataStorage dataStorage, ILogger logger)
        {
            this.dataStorage = dataStorage;
            this.logger = logger;
        }

        protected void Page_Load(object sender, EventArgs e)
        {
            var positions = dataStorage.GetCurrentPositions().GetAwaiter().GetResult().ToList();
            var users = dataStorage.GetUserInfos().GetAwaiter().GetResult().ToList();
            positionsData = positions.Select(p => (Pos: p, User: users.FirstOrDefault(u => u.Id == p.UserId)))
                .Select(item => (item.Pos, item.User.Login, item.User.Company))
                .ToList();
        }
    }
}
