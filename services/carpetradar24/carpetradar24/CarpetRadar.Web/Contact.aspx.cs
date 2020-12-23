using System;
using System.Web.UI;
using CarpetRadar.Services;
using CarpetRadar.Services.DataStorage;
using NLog;

namespace CarpetRadar.Web
{
    public partial class Contact : Page
    {
        protected readonly IDataStorage storage;
        private readonly ILogger logger;

        public Contact(IDataStorage storage, ILogger logger)
        {
            this.storage = storage;
            this.logger = logger;
        }

        protected void Page_Load(object sender, EventArgs e)
        {
            storage.GetCurrentPositions();
        }
    }
}
