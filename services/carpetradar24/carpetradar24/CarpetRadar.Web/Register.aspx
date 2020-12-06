<%@ Page Title="Register" Language="C#" MasterPageFile="~/Site.Master" AutoEventWireup="true" CodeBehind="Register.aspx.cs" Inherits="CarpetRadar.Web.Register" %>

<asp:Content ID="BodyContent" ContentPlaceHolderID="MainContent" runat="server">
    <h3>
        <font face="Verdana">Registration Page</font>
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
            <td>Company:</td>
            <td>
                <input id="txtCompanyName" type="text" runat="server"/>
            </td>
            <td>
                <ASP:RequiredFieldValidator ControlToValidate="txtCompanyName"
                                            Display="Static" ErrorMessage="*" runat="server"
                                            ID="vCompanyName"/>
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
    <input type="submit" Value="Register" runat="server" ID="cmdRegister"/>
    <p></p>
    <asp:Label id="lblMsg" ForeColor="red" Font-Name="Verdana" Font-Size="10" runat="server"/>
</asp:Content>