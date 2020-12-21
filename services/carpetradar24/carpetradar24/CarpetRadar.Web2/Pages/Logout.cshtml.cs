using Microsoft.AspNetCore.Mvc.RazorPages;

namespace CarpetRadar.Web2.Pages
{
    public class LogoutModel : PageModel
    {
        public void OnGet()
        {
            Response.Cookies.Delete("token");
        }
    }
}
