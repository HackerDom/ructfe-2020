import redis.clients.jedis.Jedis
import java.io.File
import java.util.*

class SessionManager(
    private val jedis: Jedis
) {
    init {
        jedis.connect()
    }

    fun create(username: String): String {
        val safeUsername = safeEscapeLogin(username)
        val salt = randomString()
        val secret = Base64.getEncoder().encode(stringHash(safeUsername + salt))
        jedis[safeUsername] = salt
        return String(secret)
    }

    fun delete(username: String) {
        try {
            jedis.del(username)
        } catch (e: Throwable) { }
    }

    fun validate(username: String, secret: String): Boolean {
        val safeUsername = safeEscapeLogin(username)
        try {
            val decoded = Base64.getDecoder().decode(secret)
            val salt = jedis.get(safeUsername) ?: return false
            return stringHash(safeUsername + salt).contentEquals(decoded)
        } catch (e: Throwable) {
            return false
        }
    }
}
