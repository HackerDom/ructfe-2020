import io.javalin.Javalin
import io.javalin.http.Context
import kotlinx.html.*
import java.io.File


fun App.getAuthenticatedUser(ctx: Context): String? {
    val login = ctx.cookie("login") ?: run { return null }
    val secret = ctx.cookie("secret") ?: run { return null }
    if (sessionManager.validate(login, secret)) {
        return login
    }
    return null
}


fun App.addMainHandler(): Javalin = javalin.get("/*") { ctx ->
    val authenticatedUser = getAuthenticatedUser(ctx)

    if (authenticatedUser == null) {
        ctx.withHtml {
            body {
                p {
                    +"You need to authorize "
                    a(Endpoints.REGISTER_PAGE) { +"here" }
                }
            }
        }
        ctx.contentType("text/html")
        return@get
    }

    val authenticatedUserDir = File(STORAGE_PATH).resolve(authenticatedUser)
    if (!authenticatedUserDir.exists()) {
        authenticatedUserDir.mkdirs()
    }

    val file = authenticatedUserDir.resolve(ctx.path().substring(1))
    if (!file.exists()) {
        ctx.result("Not found")
        return@get
    }

    if (file.isFile) {
        ctx.result(file.readBytes())
        return@get
    }

    if (file.isDirectory) {
        ctx.withHtml {
            body {
                ul {
                    for (name in file.list()) {
                        li {
                            a(File(ctx.path()).resolve(name).toString()) {
                                +name
                            }
                        }
                    }
                }
            }
        }
        ctx.contentType("text/html")
    }
}


fun FlowOrInteractiveOrPhrasingContent.loginAndPassword() {
    label { text("Login") }
    input(type = InputType.text, name = "login")
    br
    label { text("Password") }
    input(type = InputType.password, name = "password")
    br
}


fun App.addRegisterPageHandler(): Javalin = javalin.get(Endpoints.REGISTER_PAGE) { ctx ->
    getAuthenticatedUser(ctx)?.let {
        ctx.redirect("/")
        return@get
    }

    ctx.withHtml {
        body {
            form(action = Endpoints.REGISTER, method = FormMethod.post) {
                loginAndPassword()
                button { text("Register") }
            }
            a(href = Endpoints.LOGIN_PAGE) { +"Go to login page" }
        }
    }
    ctx.contentType("text/html")
}


fun App.addLoginPageHandler(): Javalin = javalin.get(Endpoints.LOGIN_PAGE) { ctx ->
    getAuthenticatedUser(ctx)?.let {
        ctx.redirect("/")
        return@get
    }

    ctx.withHtml {
        body {
            form(action = Endpoints.LOGIN, method = FormMethod.post) {
                loginAndPassword()
                button { text("Login") }
            }
            a(href = Endpoints.REGISTER_PAGE) { +"Go to register page" }
        }
    }
    ctx.contentType("text/html")
}


fun Context.getFormParamOrBadStatus(name: String): String? {
    return formParam(name) ?: run {
        status(400)
        null
    }
}


fun App.addLoginHandler(): Javalin = javalin.post(Endpoints.LOGIN) { ctx ->
    val login = ctx.getFormParamOrBadStatus("login") ?: run { return@post }
    val password = ctx.getFormParamOrBadStatus("password") ?: run { return@post }
    if (userStorage.isValid(login, password)) {
        authenticate(ctx, login)
    } else {
        ctx.status(403)
    }
}


fun App.authenticate(ctx: Context, login: String) {
    ctx.clearCookieStore()
    val secret = sessionManager.create(login)
    ctx.cookie("login", login)
    ctx.cookie("secret", secret)
    ctx.redirect("/")
}


fun App.addRegisterHandler(): Javalin = javalin.post(Endpoints.REGISTER) { ctx ->
    val login = ctx.getFormParamOrBadStatus("login") ?: run { return@post }
    val password = ctx.getFormParamOrBadStatus("password") ?: run { return@post }

    if (userStorage.exists(login)) {
        ctx.status(400)
        return@post
    }

    userStorage.create(login, password)
    authenticate(ctx, login)
}
