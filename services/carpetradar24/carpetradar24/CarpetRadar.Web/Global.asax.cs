using System;
using System.Web;
using System.Web.Optimization;
using System.Web.Routing;
using CarpetRadar.Services.DataStorage;
using CarpetRadar.Services.IdentityServices;
using Microsoft.AspNet.WebFormsDependencyInjection.Unity;
using NLog;
using Unity;
using Unity.Injection;

namespace CarpetRadar.Web
{
    public class Global : HttpApplication
    {
        private IUnityContainer container;

        protected void Application_Start(object sender, EventArgs e)
        {
            container = this.AddUnity();

            container.RegisterType<ILogger>(
                new InjectionFactory(c => LogManager.GetCurrentClassLogger()));

            container.RegisterType<IDataStorage>(
                new InjectionFactory(c => DataStorageBuilder.GetDefaultStorage(c.Resolve<ILogger>())));

            container.RegisterType<IRegistrationService, RegistrationService>();
            container.RegisterType<IAuthenticationService, AuthenticationService>();

            RouteConfig.RegisterRoutes(RouteTable.Routes);
            BundleConfig.RegisterBundles(BundleTable.Bundles);
        }
    }
}
