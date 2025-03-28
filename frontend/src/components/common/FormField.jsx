// frontend/src/components/common/FormField.jsx
import React from 'react';
import { Field, ErrorMessage } from 'formik';

/**
 * Componente riutilizzabile per campi di form con Formik
 * @param {Object} props - Props del componente
 * @param {string} props.name - Nome del campo
 * @param {string} props.label - Etichetta del campo
 * @param {string} props.type - Tipo di campo (text, email, password, select, textarea, checkbox, radio, multiselect)
 * @param {Array} props.options - Opzioni per select, radio, checkbox e multiselect
 * @param {Object} props.touched - Stato touched di Formik
 * @param {Object} props.errors - Errori di Formik
 * @param {string} props.placeholder - Placeholder per il campo
 * @param {boolean} props.required - Se il campo è obbligatorio
 * @param {Object} props.fieldProps - Props aggiuntive per il campo
 */
const FormField = ({ 
  name, 
  label, 
  type = 'text', 
  options = [], 
  touched, 
  errors, 
  placeholder = '',
  required = false,
  fieldProps = {}
}) => {
  // Determina se il campo ha un errore
  const hasError = touched && touched[name] && errors && errors[name];
  
  // Funzione per rendere il campo appropriato in base al tipo
  const renderField = () => {
    switch (type) {
      case 'select':
        return (
          <Field 
            as="select" 
            id={name} 
            name={name} 
            className={`form-control ${hasError ? 'has-error' : ''}`} 
            {...fieldProps}
          >
            <option value="">{placeholder || 'Seleziona...'}</option>
            {options.map(option => (
              <option 
                key={option.value} 
                value={option.value}
              >
                {option.label}
              </option>
            ))}
          </Field>
        );
        
      case 'textarea':
        return (
          <Field 
            as="textarea" 
            id={name} 
            name={name} 
            className={`form-control ${hasError ? 'has-error' : ''}`} 
            placeholder={placeholder}
            rows={fieldProps.rows || 3}
            {...fieldProps}
          />
        );
        
      case 'checkbox':
        return (
          <div className="checkbox-group">
            {options.length > 0 ? (
              // Lista di checkbox
              options.map(option => (
                <div key={option.value} className="checkbox-item">
                  <label className="checkbox-label">
                    <Field 
                      type="checkbox" 
                      name={name} 
                      value={option.value} 
                      className="checkbox-input"
                      {...fieldProps}
                    />
                    <span>{option.label}</span>
                  </label>
                </div>
              ))
            ) : (
              // Singolo checkbox
              <label className="checkbox-label">
                <Field 
                  type="checkbox" 
                  name={name} 
                  className="checkbox-input"
                  {...fieldProps}
                />
                <span>{label}</span>
              </label>
            )}
          </div>
        );
        
      case 'radio':
        return (
          <div className="radio-group">
            {options.map(option => (
              <div key={option.value} className="radio-item">
                <label className="radio-label">
                  <Field 
                    type="radio" 
                    name={name} 
                    value={option.value} 
                    className="radio-input"
                    {...fieldProps}
                  />
                  <span>{option.label}</span>
                </label>
              </div>
            ))}
          </div>
        );
        
      case 'multiselect':
        return (
          <div className="multiselect-container">
            {options.map(option => (
              <div key={option.id || option.value} className="multiselect-item">
                <label className="checkbox-label">
                  <Field 
                    type="checkbox" 
                    name={name} 
                    value={(option.id || option.value).toString()} 
                    className="checkbox-input"
                    {...fieldProps}
                  />
                  <span>{option.title || option.name || option.label}</span>
                </label>
              </div>
            ))}
          </div>
        );
        
      default:
        return (
          <Field 
            type={type} 
            id={name} 
            name={name} 
            className={`form-control ${hasError ? 'has-error' : ''}`} 
            placeholder={placeholder}
            {...fieldProps}
          />
        );
    }
  };
  
  return (
    <div className={`form-group ${hasError ? 'has-error' : ''}`}>
      {label && type !== 'checkbox' && (
        <label htmlFor={name} className="form-label">
          {label}
          {required && <span className="required-indicator">*</span>}
        </label>
      )}
      
      {renderField()}
      
      <ErrorMessage 
        name={name} 
        component="div" 
        className="error-message" 
      />
    </div>
  );
};

export default FormField;