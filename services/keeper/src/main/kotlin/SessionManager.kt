import java.io.File
import java.util.*

class SessionManager(
    storage: String
) {
    private val storage = File(storage)

    fun create(username: String): String {
        val salt = randomString()
        val secret = Base64.getEncoder().encode(stringHash(username + salt))
        storage.resolve(username).writeText(salt)
        return String(secret)
    }

    fun validate(username: String, secret: String): Boolean {
        try {
            val decoded = Base64.getDecoder().decode(secret)
            val saltFile = storage.resolve(username)
            if (!saltFile.exists()) {
                return false
            }
            val salt = saltFile.readText()
            return stringHash(username + salt).contentEquals(decoded)
        } catch (e: Throwable) {
            return false
        }
    }
}
