import redis.clients.jedis.Jedis
import redis.clients.jedis.JedisPool
import java.io.File
import java.util.*

class SessionManager(
    private val jedisPool: JedisPool
) {
    private fun <T> withJedis(block: (Jedis) -> T): T? {
        var jedis: Jedis? = null
        return try {
            jedis = jedisPool.resource
            block(jedis)
        } catch (e: Throwable) {
            e.printStackTrace()
            null
        } finally {
            jedis?.close()
        }
    }

    fun create(username: String): String {
        val safeUsername = safeEscapeLogin(username)
        val salt = randomString()
        val secret = Base64.getEncoder().encode(stringHash(safeUsername + salt))

        withJedis { jedis ->
            jedis[safeUsername] = salt
        }

        return String(secret)
    }

    fun delete(username: String) {
        try {
            withJedis { jedis ->
                jedis.del(username)
            }
        } catch (e: Throwable) { }
    }

    fun validate(username: String, secret: String): Boolean {
        val safeUsername = safeEscapeLogin(username)
        try {
            return withJedis { jedis ->
                val decoded = Base64.getDecoder().decode(secret)
                val salt = jedis.get(safeUsername) ?: return@withJedis false
                stringHash(safeUsername + salt).contentEquals(decoded)
            } ?: false
        } catch (e: Throwable) {
            return false
        }
    }
}
