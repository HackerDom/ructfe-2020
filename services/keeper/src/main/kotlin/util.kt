import io.javalin.http.Context
import kotlinx.html.HTML
import kotlinx.html.html
import kotlinx.html.stream.appendHTML
import java.security.MessageDigest

fun Context.withHtml(block : HTML.() -> Unit = {}) = res.writer.appendHTML().html {
    block()
}



const val ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


fun randomString(length: Int = 20) = (1..length)
    .map { ALPHABET.indices.random() }
    .map(ALPHABET::get)
    .joinToString("")


fun stringHash(password: String): ByteArray = MessageDigest.getInstance("SHA-256").digest(password.toByteArray())
