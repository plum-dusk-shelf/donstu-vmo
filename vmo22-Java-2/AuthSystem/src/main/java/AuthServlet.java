package main.java;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import java.io.IOException;
import java.io.PrintWriter;
import java.text.SimpleDateFormat;
import java.util.Date;

@WebServlet("/auth")
public class AuthServlet extends HttpServlet {
    private UserXMLHandler userXMLHandler;

    @Override
    public void init() throws ServletException {
        super.init();
        userXMLHandler = new UserXMLHandler();
    }

    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        response.setContentType("text/html;charset=UTF-8");
        PrintWriter out = response.getWriter();

        String login = request.getParameter("login");
        String password = request.getParameter("password");

        HttpSession session = request.getSession();

        // Проверка на блокировку после 3 неудачных попыток
        Integer attempts = (Integer) session.getAttribute("attempts");
        if (attempts != null && attempts >= 3) {
            out.println("<h2>Авторизация заблокирована после 3 неудачных попыток</h2>");
            return;
        }

        if (login == null || password == null || login.isEmpty() || password.isEmpty()) {
            out.println("<h2>Логин и пароль не могут быть пустыми</h2>");
            return;
        }

        // Простая "хэш"-функция для демонстрации
        String passwordHash = Integer.toString(password.hashCode());

        if (userXMLHandler.userExists(login)) {
            // Авторизация
            User user = userXMLHandler.findUser(login);
            if (user.getPasswordHash().equals(passwordHash)) {
                // Успешная авторизация
                session.removeAttribute("attempts");

                SimpleDateFormat sdf = new SimpleDateFormat("dd.MM.yyyy HH:mm:ss");
                String currentTime = sdf.format(new Date());

                out.println("<h2>Авторизация успешна!</h2>");
                out.println("<p>Текущая дата и время сервера: " + currentTime + "</p>");
            } else {
                // Неправильный пароль
                incrementAttempts(session);
                attempts = (Integer) session.getAttribute("attempts");

                out.println("<h2>Неправильный логин или пароль</h2>");
                out.println("<p>Попытка #" + attempts + "</p>");

                if (attempts >= 3) {
                    out.println("<p style='color: red;'>Авторизация заблокирована после 3 неудачных попыток</p>");
                }
            }
        } else {
            // Регистрация нового пользователя
            User newUser = new User(login, passwordHash);
            userXMLHandler.addUser(newUser);

            SimpleDateFormat sdf = new SimpleDateFormat("dd.MM.yyyy HH:mm:ss");
            String currentTime = sdf.format(new Date());

            out.println("<h2>Регистрация успешна!</h2>");
            out.println("<p>Текущая дата и время сервера: " + currentTime + "</p>");
        }
    }

    private void incrementAttempts(HttpSession session) {
        Integer attempts = (Integer) session.getAttribute("attempts");
        if (attempts == null) {
            attempts = 1;
        } else {
            attempts++;
        }
        session.setAttribute("attempts", attempts);
    }
}