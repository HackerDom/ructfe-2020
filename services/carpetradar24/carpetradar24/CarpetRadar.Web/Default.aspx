<%@ Page Title="Home Page" Language="C#" MasterPageFile="~/Site.Master" AutoEventWireup="true" CodeBehind="Default.aspx.cs" Inherits="CarpetRadar.Web._Default" %>

<asp:Content ID="BodyContent" ContentPlaceHolderID="MainContent" runat="server">

    <div class="jumbotron">
        <h1>ASP.NET</h1>
        <p class="lead">ASP.NET is a free web framework for building great Web sites and Web applications using HTML, CSS, and JavaScript.</p>
        <p>
            <a href="http://www.asp.net" class="btn btn-primary btn-lg">Learn more &raquo;</a>
        </p>
    </div>

    <div class="row">
        <div class="col-md-4">
            <h2>Getting started</h2>
            <p>
                ASP.NET Web Forms lets you build dynamic websites using a familiar drag-and-drop, event-driven model.
                A design surface and hundreds of controls and components let you rapidly build sophisticated, powerful UI-driven sites with data access.
            </p>
            <p>
                <a class="btn btn-default" href="https://go.microsoft.com/fwlink/?LinkId=301948">Learn more &raquo;</a>
            </p>
        </div>
        <div class="col-md-4">
            <h2>Get more libraries</h2>
            <p>
                NuGet is a free Visual Studio extension that makes it easy to add, remove, and update libraries and tools in Visual Studio projects.
            </p>
            <p>
                <a class="btn btn-default" href="https://go.microsoft.com/fwlink/?LinkId=301949">Learn more &raquo;</a>
            </p>
        </div>
        <div class="col-md-4">
            <h2>Web Hosting</h2>
            <p>
                You can easily find a web hosting company that offers the right mix of features and price for your applications.
            </p>
            <p>
                <a class="btn btn-default" href="https://go.microsoft.com/fwlink/?LinkId=301950">Learn more &raquo;</a>
            </p>
        </div>
    </div>


    <h3> Now there are <% Response.Write(positionsData.Count(d => !d.Position.Finished)); %> magic carpets in the air</h3>
    <table>
        <thead>
        <tr>
            <th>Aerial vehicle</th>
            <th>Location</th>
            <th>Last connection time</th>
            <th>Company</th>
            <th>Contact address</th>
        </tr>
        </thead>
        <tbody>
        <%
            foreach (var cp in positionsData.Where(d => !d.Position.Finished))
            {
                string htmlString = "<tr>" +
                                    $"<td>{cp.Position.Label}</td>" +
                                    $"<td>({cp.Position.X}; {cp.Position.Y})</td>" +
                                    $"<td>-</td>" +
                                    $"<td>{cp.Company}</td>" +
                                    $"<td>{cp.Login}@carpetradar24.ru</td>" +
                                    "<tr/>";
                Response.Write(htmlString);
            } %>
        </tbody>
    </table>
</asp:Content>