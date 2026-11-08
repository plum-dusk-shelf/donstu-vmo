package main.java;

import java.io.IOException;
import java.io.PrintWriter;
import java.text.SimpleDateFormat;
import java.util.Date;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

@WebServlet("/SessionInfoServlet")
public class SessionInfoServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private static final SimpleDateFormat timeFormat = new SimpleDateFormat("HH:mm:ss");
    private static final SimpleDateFormat dateTimeFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        // Установка типа содержимого ответа
        response.setContentType("text/html;charset=UTF-8");

        // Получение сессии (или создание новой, если не существует)
        HttpSession session = request.getSession(true);

        // Увеличение счетчика запросов в сессии
        Integer requestCount = (Integer) session.getAttribute("requestCount");
        if (requestCount == null) {
            requestCount = 1;
        } else {
            requestCount++;
        }
        session.setAttribute("requestCount", requestCount);

        // Получение времени создания сессии
        long creationTime = session.getCreationTime();
        Date creationDate = new Date(creationTime);

        // Текущее время на сервере
        Date now = new Date();

        // Генерация HTML-страницы
        try (PrintWriter out = response.getWriter()) {
            out.println("<!DOCTYPE html>");
            out.println("<html>");
            out.println("<head>");
            out.println("<title>Информация о сессии</title>");
            out.println("<style>");
            out.println("body { font-family: Arial, sans-serif; margin: 40px; }");
            out.println("h1 { color: #333; }");
            out.println("table { border-collapse: collapse; width: 100%; max-width: 600px; margin: 20px 0; }");
            out.println("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }");
            out.println("th { background-color: #f2f2f2; }");
            out.println("</style>");
            out.println("</head>");
            out.println("<body>");
            out.println("<h1>Информация о сессии</h1>");
            out.println("<table>");
            out.println("<tr><th>Параметр</th><th>Значение</th></tr>");
            out.println("<tr><td>ID сессии</td><td>" + session.getId() + "</td></tr>");
            out.println("<tr><td>Время создания сессии</td><td>" + dateTimeFormat.format(creationDate) + "</td></tr>");
            out.println("<tr><td>Текущее время на сервере</td><td>" + dateTimeFormat.format(now) + "</td></tr>");
            out.println("<tr><td>Количество запросов в сессии</td><td>" + requestCount + "</td></tr>");
            out.println("<tr><td>Время последнего доступа</td><td>" + dateTimeFormat.format(new Date(session.getLastAccessedTime())) + "</td></tr>");
            out.println("<tr><td>Макс. время бездействия (сек)</td><td>" + session.getMaxInactiveInterval() + "</td></tr>");
            out.println("</table>");
            out.println("<p><a href=\"SessionInfoServlet\">Обновить страницу</a></p>");
            out.println("</body>");
            out.println("</html>");
        }
    }
}