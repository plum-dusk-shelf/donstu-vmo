package main.java;

import jakarta.servlet.*;
import jakarta.servlet.http.*;
import jakarta.servlet.annotation.*;
import java.io.*;
import java.net.*;
import java.text.*;
import java.util.*;
import org.json.*;

@WebServlet("/currency")
public class CurrencyServlet extends HttpServlet {
    private static final String CBR_API_URL = "https://www.cbr-xml-daily.ru/daily_json.js";
    private static final String CBR_METALS_API = "https://www.cbr-xml-daily.ru/daily_metals_json.js";
    private static final SimpleDateFormat DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd");
    private static final SimpleDateFormat DISPLAY_DATE_FORMAT = new SimpleDateFormat("dd.MM.yyyy");

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        response.setContentType("text/html;charset=UTF-8");
        PrintWriter out = response.getWriter();

        try {
            String dateParam = request.getParameter("date");
            String startDateParam = request.getParameter("startDate");
            String endDateParam = request.getParameter("endDate");
            String currencyType = request.getParameter("currencyType");

            // Определяем, запрашивается ли период или конкретная дата
            boolean isPeriod = startDateParam != null && !startDateParam.isEmpty() &&
                    endDateParam != null && !endDateParam.isEmpty();

            out.println("<!DOCTYPE html>");
            out.println("<html><head>");
            out.println("<title>Результаты запроса котировок</title>");
            out.println("<style>");
            out.println("body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }");
            out.println("table { width: 100%; border-collapse: collapse; margin-top: 20px; }");
            out.println("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }");
            out.println("th { background-color: #f2f2f2; }");
            out.println("h1 { color: #333; }");
            out.println(".info { margin-bottom: 20px; }");
            out.println("</style>");
            out.println("</head><body>");
            out.println("<h1>Котировки ЦБ РФ</h1>");

            if (dateParam != null && !dateParam.isEmpty() && !isPeriod) {
                // Запрос для одной даты
                Date date = DATE_FORMAT.parse(dateParam);
                String formattedDate = DISPLAY_DATE_FORMAT.format(date);
                out.println("<div class='info'>Данные на дату: " + formattedDate + "</div>");

                String apiUrl = currencyType.equals("metals") ? CBR_METALS_API : CBR_API_URL;
                String jsonData = fetchDataFromCbr(apiUrl, dateParam);

                if (currencyType.equals("metals")) {
                    displayMetalsData(out, jsonData);
                } else {
                    displayCurrencyData(out, jsonData);
                }
            } else if (isPeriod) {
                // Запрос за период
                Date startDate = DATE_FORMAT.parse(startDateParam);
                Date endDate = DATE_FORMAT.parse(endDateParam);

                if (startDate.after(endDate)) {
                    out.println("<div class='error'>Ошибка: Начальная дата должна быть раньше конечной</div>");
                } else {
                    String formattedStartDate = DISPLAY_DATE_FORMAT.format(startDate);
                    String formattedEndDate = DISPLAY_DATE_FORMAT.format(endDate);
                    out.println("<div class='info'>Данные за период с " + formattedStartDate +
                            " по " + formattedEndDate + "</div>");

                    // Для простоты примера будем получать данные только для конечной даты
                    // В реальном приложении нужно реализовать получение данных за каждый день периода
                    String apiUrl = currencyType.equals("metals") ? CBR_METALS_API : CBR_API_URL;
                    String jsonData = fetchDataFromCbr(apiUrl, endDateParam);

                    if (currencyType.equals("metals")) {
                        displayMetalsData(out, jsonData);
                    } else {
                        displayCurrencyData(out, jsonData);
                    }

                    out.println("<div class='info'>Примечание: В этом примере показаны данные только для конечной даты периода. " +
                            "В реальном приложении следует реализовать получение данных за каждый день периода.</div>");
                }
            } else {
                out.println("<div class='error'>Ошибка: Не указана дата или период</div>");
            }

            out.println("<div style='margin-top: 20px;'><a href='/'>Новый запрос</a></div>");
            out.println("</body></html>");
        } catch (Exception e) {
            out.println("<div class='error'>Ошибка: " + e.getMessage() + "</div>");
            e.printStackTrace(out);
        } finally {
            out.close();
        }
    }

    private String fetchDataFromCbr(String apiUrl, String date) throws IOException {
        // В реальном приложении нужно формировать URL с учетом даты
        // API ЦБ РФ имеет ограничения, для исторических данных может потребоваться другой подход
        URL url = new URL(apiUrl);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");

        StringBuilder response = new StringBuilder();
        try (BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()))) {
            String line;
            while ((line = in.readLine()) != null) {
                response.append(line);
            }
        }

        return response.toString();
    }

    private void displayCurrencyData(PrintWriter out, String jsonData) throws JSONException {
        JSONObject json = new JSONObject(jsonData);
        JSONObject valutes = json.getJSONObject("Valute");

        out.println("<table>");
        out.println("<tr><th>Код</th><th>Название</th><th>Номинал</th><th>Курс</th><th>Изменение</th></tr>");

        Iterator<String> keys = valutes.keys();
        while (keys.hasNext()) {
            String key = keys.next();
            JSONObject valute = valutes.getJSONObject(key);

            String charCode = valute.getString("CharCode");
            String name = valute.getString("Name");
            int nominal = valute.getInt("Nominal");
            double value = valute.getDouble("Value");
            double previous = valute.getDouble("Previous");
            double change = value - previous;

            out.printf("<tr><td>%s</td><td>%s</td><td>%d</td><td>%.4f</td><td style='color: %s;'>%.4f</td></tr>",
                    charCode, name, nominal, value,
                    change >= 0 ? "green" : "red", change);
        }

        out.println("</table>");
    }

    private void displayMetalsData(PrintWriter out, String jsonData) throws JSONException {
        JSONObject json = new JSONObject(jsonData);
        JSONObject metals = json.getJSONObject("Metals");

        out.println("<table>");
        out.println("<tr><th>Металл</th><th>Код</th><th>Цена (руб/грамм)</th><th>Изменение</th></tr>");

        Iterator<String> keys = metals.keys();
        while (keys.hasNext()) {
            String key = keys.next();
            JSONObject metal = metals.getJSONObject(key);

            String code = metal.getString("Code");
            String name = metal.getString("Name");
            double price = metal.getDouble("Price");
            double previous = metal.getDouble("Previous");
            double change = price - previous;

            out.printf("<tr><td>%s</td><td>%s</td><td>%.2f</td><td style='color: %s;'>%.2f</td></tr>",
                    name, code, price,
                    change >= 0 ? "green" : "red", change);
        }

        out.println("</table>");
    }
}
