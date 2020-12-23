<%@ Page Title="Login" Language="C#" MasterPageFile="~/Site.Master" AutoEventWireup="true" CodeBehind="Login.aspx.cs" Inherits="CarpetRadar.Web.Login" %>

<asp:Content ID="BodyContent" ContentPlaceHolderID="MainContent" runat="server">
    <h3>
        <font face="Verdana">Login Page</font>
    </h3>
    <table>
        <tr>
            <td>Login:</td>
            <td>
                <input id="txtUserName" type="text" runat="server"/>
            </td>
            <td>
                <ASP:RequiredFieldValidator ControlToValidate="txtUserName"
                                            Display="Static" ErrorMessage="*" runat="server"
                                            ID="vUserName"/>
            </td>
        </tr>
        <tr>
            <td>Password:</td>
            <td>
                <input id="txtUserPass" type="password" runat="server"/>
            </td>
            <td>
                <ASP:RequiredFieldValidator ControlToValidate="txtUserPass"
                                            Display="Static" ErrorMessage="*" runat="server"
                                            ID="vUserPass"/>
            </td>
        </tr>
        <tr>
            <td>Persistent Cookie:</td>
            <td>
                <ASP:CheckBox id="chkPersistCookie" runat="server" autopostback="false"/>
            </td>
            <td></td>
        </tr>
    </table>
    <input type="submit" Value="Login" runat="server" ID="cmdLogin"/>
    <p></p>
    <asp:Label id="lblMsg" ForeColor="red" Font-Name="Verdana" Font-Size="10" runat="server"/>
</asp:Content>