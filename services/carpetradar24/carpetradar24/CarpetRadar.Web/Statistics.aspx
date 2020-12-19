<%@ Page Title="Statistics" Language="C#" MasterPageFile="~/Site.Master" AutoEventWireup="true" CodeBehind="Statistics.aspx.cs" Inherits="CarpetRadar.Web.Statistics" %>
<%@ Import Namespace="System.Runtime.CompilerServices" %>

<asp:Content ID="BodyContent" ContentPlaceHolderID="MainContent" runat="server">
    <h2><%: Title %>.</h2>
    <h3>Your application description page.</h3>
    <p><% //var userData = dataStorage.FindUser(); %></p>
    <h2></h2>
    <p>
        <b>Login:</b> <%: userInfo.Login %>
    </p>
    <p>
        <b>Company:</b> <%: userInfo.Company %>
    </p>
    <p>
        <b></b>
    </p>
    <p>
        <b></b>
    </p>
    <h3>Your magic flights</h3>
    <table>
        <thead>
        <tr>
            <th>Aerial vehicle</th>
            <th>License</th>
            <th>Start location</th>
            <th>Last location</th>
            <th>Total distance</th>
            <th>Start time</th>
            <th>Last time</th>
            <th>Total travel time</th>
            <th>Is flight finished</th>
        </tr>
        </thead>
        <tbody>
        <%
            foreach (var cp in userFlights)
            {
                var totalDistance = cp.X.Zip(cp.Y, (x, y) => Math.Sqrt((double) x * x + (double) y * y)).Sum();
                var totalTime = (cp.ReportMoments.Last() - cp.ReportMoments.First());
                var htmlString =
                    "<tr>" +
                    $"<td>{cp.Label}</td>" +
                    $"<td>{cp.License}</td>" +
                    $"<td>({cp.X.First()}; {cp.Y.First()})</td>" +
                    $"<td>({cp.X.Last()}; {cp.Y.Last()})</td>" +
                    $"<td>{totalDistance}</td>" +
                    $"<td>{cp.ReportMoments.First()}</td>" +
                    $"<td>{cp.ReportMoments.Last()}</td>" +
                    $"<td>{totalTime}</td>" +
                    $"<td>{cp.Finished}</td>" +
                    "<tr/>";
                Response.Write(htmlString);
            } %>
        </tbody>
    </table>
</asp:Content>