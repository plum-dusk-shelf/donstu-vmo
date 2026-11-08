package com.lab5;

//import javax.enterprise.context.SessionScoped;
import jakarta.inject.Named;
//import javax.inject.Named;
import java.io.Serializable;
import jakarta.inject.Named;
import jakarta.enterprise.context.SessionScoped;
import jakarta.faces.application.FacesMessage;
import jakarta.faces.component.UIComponent;
import jakarta.faces.context.FacesContext;
import jakarta.faces.validator.FacesValidator;
import jakarta.faces.validator.Validator;
import jakarta.faces.validator.ValidatorException;

@Named
@SessionScoped
public class AuthBean implements Serializable {
    private String login;
    private String password;
    
    // Getters and Setters
    public String getLogin() {
        return login;
    }
    
    public void setLogin(String login) {
        this.login = login;
    }
    
    public String getPassword() {
        return password;
    }
    
    public void setPassword(String password) {
        this.password = password;
    }
    
    public String authenticate() {
        // Здесь должна быть логика проверки учетных данных
        return "welcome?faces-redirect=true";
    }
}
