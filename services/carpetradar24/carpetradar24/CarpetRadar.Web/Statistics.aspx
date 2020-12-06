<%@ Page Title="Statistics" Language="C#" MasterPageFile="~/Site.Master" AutoEventWireup="true" CodeBehind="Statistics.aspx.cs" Inherits="CarpetRadar.Web.Statistics" %>

<asp:Content ID="BodyContent" ContentPlaceHolderID="MainContent" runat="server">
    <h2><%: Title %>.</h2>
    <h3>Your application description page.</h3>
    <p><% //var userData = dataStorage.FindUser(); %></p>
    <h2></h2>
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
        <% var flights = dataStorage.GetCurrentPositions().GetAwaiter().GetResult();
           foreach (var fl in flights)
           {
               string htmlString = "<tr>" +
                                   $"<td>{fl.Label}</td>" +
                                   $"<td>{fl.X}</td>" +
                                   $"<td>{fl.Y}</td>" +
                                   "<tr/>";
               Response.Write(htmlString);
           } %>
        </tbody>
    </table>
</asp:Content>