package main.java.controller;

import main.java.dao.ProductDao;
import main.java.model.Product;
import main.java.dao.ManufacturerDao;
import main.java.model.Manufacturer;
import main.java.dao.CategoryDao;
import main.java.model.Category;
import jakarta.servlet.*;
import jakarta.servlet.http.*;
import jakarta.servlet.annotation.*;
import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.List;

@WebServlet(name = "ProductController", urlPatterns = {"/products"})
public class ProductController extends HttpServlet {
    private ProductDao productDao;
	private CategoryDao categoryDao;    // Добавьте это
    private ManufacturerDao manufacturerDao;
    
    @Override
public void init() throws ServletException {
    try {
        Class.forName("org.postgresql.Driver");
        Connection connection = DriverManager.getConnection(
            "jdbc:postgresql://localhost:5432/inventory_db",
            "postgres", "password");
            
        // Инициализируем все DAO
        productDao = new ProductDao(connection);
        categoryDao = new CategoryDao(connection);          // Добавьте это
        manufacturerDao = new ManufacturerDao(connection);  // Добавьте это
        
    } catch (ClassNotFoundException | SQLException e) {
        throw new ServletException(e);
    }
}

    
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException {
        String action = request.getParameter("action");
        
        try {
            if (action == null || action.isEmpty()) {
                listProducts(request, response);
            } else {
                switch (action) {
                    case "new":
                        showNewForm(request, response);
                        break;
                    case "edit":
                        showEditForm(request, response);
                        break;
                    case "delete":
                        deleteProduct(request, response);
                        break;
                    default:
                        listProducts(request, response);
                        break;
                }
            }
        } catch (SQLException ex) {
            throw new ServletException(ex);
        }
    }
    
    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException {
        String action = request.getParameter("action");
        
        try {
            if ("insert".equals(action)) {
                insertProduct(request, response);
            } else if ("update".equals(action)) {
                updateProduct(request, response);
            }
        } catch (SQLException ex) {
            throw new ServletException(ex);
        }
    }
    
	private void listProducts(HttpServletRequest request, HttpServletResponse response)
        throws SQLException, ServletException, IOException {
    try {
        // 1. Получаем данные из DAO
        List<Product> products = productDao.getAllProducts();
        
        // 2. Логирование для отладки
        System.out.println("Получено товаров: " + products.size());
        products.forEach(p -> System.out.println(p.getName()));
        
        // 3. Устанавливаем атрибуты запроса
        request.setAttribute("products", products);
        
        // 4. Проверяем существование JSP-файла
        
        // 5. Перенаправляем на JSP
        RequestDispatcher dispatcher = request.getRequestDispatcher("/WEB-INF/views/list-products.jsp");
        dispatcher.forward(request, response);
        
    } catch (Exception e) {
        // Логируем полную ошибку
        System.err.println("Ошибка в listProducts:");
        e.printStackTrace();
        
        // Показываем пользователю сообщение об ошибке
        response.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR, 
            "Ошибка при загрузке списка товаров: " + e.getMessage());
    }
} 
    private void showNewForm(HttpServletRequest request, HttpServletResponse response)
        throws ServletException, IOException {
    try {
        // Получаем списки категорий и производителей
        List<Category> categories = categoryDao.getAllCategories();
        List<Manufacturer> manufacturers = manufacturerDao.getAllManufacturers();
        
        // Устанавливаем атрибуты запроса
        request.setAttribute("categories", categories);
        request.setAttribute("manufacturers", manufacturers);
        
        // Перенаправляем на JSP
        RequestDispatcher dispatcher = request.getRequestDispatcher("/WEB-INF/views/add-product.jsp");
        dispatcher.forward(request, response);
    } catch (SQLException e) {
        throw new ServletException("Ошибка при загрузке данных для формы", e);
    }
}
    
    private void showEditForm(HttpServletRequest request, HttpServletResponse response)
            throws SQLException, ServletException, IOException {
        int id = Integer.parseInt(request.getParameter("id"));
        Product product = productDao.getProductById(id);
        request.setAttribute("product", product);
        RequestDispatcher dispatcher = request.getRequestDispatcher("/WEB-INF/views/edit-product.jsp");
        dispatcher.forward(request, response);
    }
    
    private void insertProduct(HttpServletRequest request, HttpServletResponse response)
            throws SQLException, IOException {
        Product newProduct = extractProductFromRequest(request);
        productDao.addProduct(newProduct);
        response.sendRedirect("products");
    }
    
    private void updateProduct(HttpServletRequest request, HttpServletResponse response)
            throws SQLException, IOException {
        Product product = extractProductFromRequest(request);
        product.setId(Integer.parseInt(request.getParameter("id")));
        productDao.updateProduct(product);
        response.sendRedirect("products");
    }
    
	private void deleteProduct(HttpServletRequest request, HttpServletResponse response) 
        throws IOException {
    int id = Integer.parseInt(request.getParameter("id"));
    try {
        if (productDao.deleteProduct(id)) {
            response.sendRedirect("products");
        } else {
            response.sendError(HttpServletResponse.SC_NOT_FOUND, 
                "Товар не найден");
        }
    } catch (SQLException e) {
        response.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR,
            "Ошибка при удалении: " + e.getMessage());
    }
}
    
    private Product extractProductFromRequest(HttpServletRequest request) {
        Product product = new Product();
        product.setName(request.getParameter("name"));
        product.setDescription(request.getParameter("description"));
        product.setPrice(Double.parseDouble(request.getParameter("price")));
        product.setCategoryId(Integer.parseInt(request.getParameter("categoryId")));
        product.setManufacturerId(Integer.parseInt(request.getParameter("manufacturerId")));
        return product;
    }
    
    @Override
    public void destroy() {
        try {
            if (productDao != null) {
                productDao.close();
            }
        } catch (SQLException e) {
            System.err.println("Error closing database connection: " + e.getMessage());
        }
    }
}
