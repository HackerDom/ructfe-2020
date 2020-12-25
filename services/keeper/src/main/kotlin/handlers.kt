import io.javalin.Javalin
import io.javalin.http.Context
import kotlinx.html.*
import java.io.File
import kotlin.math.min

const val MAX_FILE_SIZE = 10240
const val MAX_FILE_COUNT_IN_RESPONSE = 1024
val loginRegex = "[a-zA-Z0-9]{3,30}".toRegex()


fun App.getAuthenticatedUser(ctx: Context): String? {
    val login = ctx.cookie("login") ?: run { return null }
    val secret = ctx.cookie("secret") ?: run { return null }
    if (sessionManager.validate(login, secret)) {
        return login
    }
    return null
}


fun App.checkFilesAccess(ctx: Context): File? {
    val authenticatedUser = getAuthenticatedUser(ctx)

    if (authenticatedUser == null) {
        ctx.status(403)
        return null
    }

    val authenticatedUserDir = File(STORAGE_PATH).resolve(authenticatedUser)
    if (!authenticatedUserDir.exists()) {
        authenticatedUserDir.mkdirs()
    }

    if (!ctx.path().startsWith(OtherConstants.FILES_PATH)) {
        ctx.status(400)
        return null
    }

    return authenticatedUserDir
}


fun App.addFilesHandler(): Javalin = javalin.get("/files/*") { ctx ->
    val authenticatedUserDir = checkFilesAccess(ctx) ?: return@get

    val lastPath = ctx.path().substring(OtherConstants.FILES_PATH.length)

    val file = authenticatedUserDir.resolve(lastPath)
    if (!file.exists()) {
        ctx.result("File already exists")
        ctx.status(400)
        return@get
    }

    if (file.isFile) {
        ctx.result(file.readBytes())
        return@get
    }

    if (file.isDirectory) {
        val offset = maxOf(ctx.queryParam("offset")?.toIntOrNull() ?: 0, 0)
        val result = (file.list() ?: emptyArray()) as Array<String>
        val left = min(result.size, offset)
        val right = min(result.size, offset + MAX_FILE_COUNT_IN_RESPONSE)
        ctx.json(result.sliceArray(left until right))
        return@get
    }
}


fun App.addUploadFilesHandler(): Javalin = javalin.post("/files/*") { ctx ->
    val authenticatedUserDir = checkFilesAccess(ctx) ?: return@post
    val newFile = try {
        ctx.uploadedFile("file")
    } catch (e: IllegalStateException) {
        ctx.result("Invalid uploading format")
        ctx.status(400)
        return@post
    }

    val lastPath = ctx.path().substring(OtherConstants.FILES_PATH.length).split("/").singleOrNull() ?: run {
        ctx.result("Incorrect path")
        ctx.status(400)
        return@post
    }

    val file = authenticatedUserDir.resolve(lastPath)
    if (file.exists()) {
        ctx.result("File already exists")
        ctx.status(400)
        return@post
    }

    if (newFile == null) {
        file.mkdirs()
        return@post
    }

    if (newFile.size > MAX_FILE_SIZE) {
        ctx.result("File is too big")
        ctx.status(400)
        return@post
    }
    file.writeBytes(newFile.content.readAllBytes())
}


fun App.addIndexHandler(): Javalin = javalin.get("/") { ctx ->
    ctx.redirect("/main")
}


fun App.addMainHandler(): Javalin = javalin.get("/main") { ctx ->
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

    ctx.withHtml {
        head {
            script {
                unsafe {
                    +"let path = [];"
                    +"let username = \"$authenticatedUser\";"
                    +"let cmd_prompt = \"$authenticatedUser@keeper:~ \";"
                }
            }
            script(null, "https://code.jquery.com/jquery-3.2.1.min.js") {}
            script(null, "https://cdnjs.cloudflare.com/ajax/libs/jquery.terminal/2.20.1/js/jquery.terminal.min.js") {}
            script(null, "/js/main.js") {}
            link(
                href = "https://cdnjs.cloudflare.com/ajax/libs/jquery.terminal/2.20.1/css/jquery.terminal.min.css",
                rel = "stylesheet"
            )
            link(href = "/css/main.css", rel = "stylesheet")
        }
        body {
            div { id = "terminal" }
            input(type = InputType.file) { id = "ufile" }
        }
    }
    ctx.contentType("text/html")
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


fun App.addRegisterHandler(): Javalin = javalin.post(Endpoints.REGISTER) { ctx ->
    val login = ctx.getFormParamOrBadStatus("login") ?: run {
        ctx.result("Can not get login from form data")
        ctx.status(400)
        return@post
    }
    if (loginRegex.find(login) == null) {
        ctx.result("Incorrect login")
        ctx.status(400)
        return@post
    }
    File(STORAGE_PATH).resolve(safeEscapeLogin(login)).mkdirs()

    val password = ctx.getFormParamOrBadStatus("password") ?: run {
        ctx.result("Can not get password from form data")
        ctx.status(400)
        return@post
    }

    if (userStorage.exists(login)) {
        ctx.result("Login already exists")
        ctx.status(400)
        return@post
    }

    if (login.length > 30 || password.length > 30) {
        ctx.result("Too long login or password")
        ctx.status(400)
        return@post
    }
    userStorage.create(login, password)
    authenticate(ctx, login)
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


fun App.addLogoutHandler(): Javalin = javalin.post(Endpoints.LOGOUT) { ctx ->
    val authenticatedUser = getAuthenticatedUser(ctx)

    if (authenticatedUser == null) {
        ctx.status(400)
        return@post
    }

    sessionManager.delete(authenticatedUser)
}


fun App.authenticate(ctx: Context, login: String) {
    ctx.clearCookieStore()
    val secret = sessionManager.create(login)
    ctx.cookie("login", login)
    ctx.cookie("secret", secret)
    ctx.redirect("/main")
}
