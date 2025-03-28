// frontend/src/components/patterns/PatternForm.jsx
import React, { useState, useEffect } from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { FaExclamationTriangle, FaSave, FaTimes } from 'react-icons/fa';

// Schema di validazione per i pattern
const PatternSchema = Yup.object().shape({
  title: Yup.string()
    .min(3, 'Il titolo deve essere di almeno 3 caratteri')
    .max(255, 'Il titolo non può superare i 255 caratteri')
    .required('Il titolo è obbligatorio'),
  description: Yup.string()
    .min(10, 'La descrizione deve essere di almeno 10 caratteri')
    .required('La descrizione è obbligatoria'),
  context: Yup.string()
    .min(10, 'Il contesto deve essere di almeno 10 caratteri')
    .required('Il contesto è obbligatorio'),
  problem: Yup.string()
    .min(10, 'Il problema deve essere di almeno 10 caratteri')
    .required('Il problema è obbligatorio'),
  solution: Yup.string()
    .min(10, 'La soluzione deve essere di almeno 10 caratteri')
    .required('La soluzione è obbligatoria'),
  consequences: Yup.string()
    .min(10, 'Le conseguenze devono essere di almeno 10 caratteri')
    .required('Le conseguenze sono obbligatorie'),
  strategy: Yup.string()
    .required('La strategia è obbligatoria'),
  mvc_component: Yup.string()
    .required('Il componente MVC è obbligatorio'),
  gdpr_ids: Yup.array(),
  pbd_ids: Yup.array(),
  iso_ids: Yup.array(),
  vulnerability_ids: Yup.array()
});

const PatternForm = ({ 
  initialValues, 
  onSubmit, 
  isEdit = false, 
  gdprArticles = [], 
  pbdPrinciples = [], 
  isoPhases = [], 
  vulnerabilities = [],
  onCancel 
}) => {
  const [error, setError] = useState(null);
  
  // Valori predefiniti per un nuovo pattern
  const defaultValues = {
    title: '',
    description: '',
    context: '',
    problem: '',
    solution: '',
    consequences: '',
    strategy: '',
    mvc_component: '',
    gdpr_ids: [],
    pbd_ids: [],
    iso_ids: [],
    vulnerability_ids: []
  };
  
  // Combinare i valori iniziali con i valori predefiniti
  const formInitialValues = { ...defaultValues, ...initialValues };
  
  // Opzioni per i dropdown
  const strategyOptions = [
    { value: 'Minimize', label: 'Minimize' },
    { value: 'Hide', label: 'Hide' },
    { value: 'Separate', label: 'Separate' },
    { value: 'Aggregate', label: 'Aggregate' },
    { value: 'Inform', label: 'Inform' },
    { value: 'Control', label: 'Control' },
    { value: 'Enforce', label: 'Enforce' },
    { value: 'Demonstrate', label: 'Demonstrate' }
  ];
  
  const mvcOptions = [
    { value: 'Model', label: 'Model' },
    { value: 'View', label: 'View' },
    { value: 'Controller', label: 'Controller' }
  ];

  // Gestore di submit con gestione errori
  const handleSubmit = async (values, { setSubmitting }) => {
    setError(null);
    try {
      await onSubmit(values);
    } catch (err) {
      setError(err.message || 'Si è verificato un errore durante il salvataggio del pattern');
      console.error('Errore nel form del pattern:', err);
    } finally {
      setSubmitting(false);
    }
  };

  // Componente per il rendering di un campo form
  const FormField = ({ name, label, type = 'text', options = [], touched, errors, as }) => (
    <div className={`form-group ${touched[name] && errors[name] ? 'has-error' : ''}`}>
      <label htmlFor={name}>{label}</label>
      
      {type === 'select' ? (
        <Field as="select" id={name} name={name} className="form-control">
          <option value="">Seleziona...</option>
          {options.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </Field>
      ) : type === 'textarea' ? (
        <Field as="textarea" id={name} name={name} className="form-control" rows="5" />
      ) : type === 'multiselect' ? (
        <div className="multiselect-container">
          {options.map(option => (
            <div key={option.id} className="multiselect-item">
              <label className="checkbox-label">
                <Field 
                  type="checkbox" 
                  name={name} 
                  value={option.id.toString()} 
                  className="checkbox-input"
                />
                <span>{option.title || option.name}</span>
              </label>
            </div>
          ))}
        </div>
      ) : (
        <Field type={type} id={name} name={name} className="form-control" />
      )}
      
      <ErrorMessage name={name} component="div" className="error-message" />
    </div>
  );

  return (
    <div className="pattern-form-container">
      {error && (
        <div className="form-error-message">
          <FaExclamationTriangle />
          <span>{error}</span>
        </div>
      )}
      
      <Formik
        initialValues={formInitialValues}
        validationSchema={PatternSchema}
        onSubmit={handleSubmit}
        enableReinitialize
      >
        {({ isSubmitting, touched, errors, setFieldValue, values }) => (
          <Form className="pattern-form">
            <div className="form-row">
              <div className="form-col">
                <FormField 
                  name="title" 
                  label="Titolo" 
                  touched={touched} 
                  errors={errors} 
                />
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-col">
                <FormField 
                  name="strategy" 
                  label="Strategia" 
                  type="select" 
                  options={strategyOptions} 
                  touched={touched} 
                  errors={errors} 
                />
              </div>
              <div className="form-col">
                <FormField 
                  name="mvc_component" 
                  label="Componente MVC" 
                  type="select" 
                  options={mvcOptions} 
                  touched={touched} 
                  errors={errors} 
                />
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-col">
                <FormField 
                  name="description"
                  label="Descrizione" 
                  type="textarea" 
                  touched={touched} 
                  errors={errors} 
                />
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-col">
                <FormField 
                  name="context" 
                  label="Contesto" 
                  type="textarea" 
                  touched={touched} 
                  errors={errors} 
                />
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-col">
                <FormField 
                  name="problem" 
                  label="Problema" 
                  type="textarea" 
                  touched={touched} 
                  errors={errors} 
                />
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-col">
                <FormField 
                  name="solution" 
                  label="Soluzione" 
                  type="textarea" 
                  touched={touched} 
                  errors={errors} 
                />
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-col">
                <FormField 
                  name="consequences" 
                  label="Conseguenze" 
                  type="textarea" 
                  touched={touched} 
                  errors={errors} 
                />
              </div>
            </div>
            
            <div className="form-section">
              <h3 className="form-section-title">Relazioni</h3>
              
              <div className="form-row">
                <div className="form-col">
                  <label>Articoli GDPR</label>
                  <FormField 
                    name="gdpr_ids"
                    label="" 
                    type="multiselect" 
                    options={gdprArticles} 
                    touched={touched} 
                    errors={errors} 
                  />
                </div>
                
                <div className="form-col">
                  <label>Principi Privacy by Design</label>
                  <FormField 
                    name="pbd_ids"
                    label="" 
                    type="multiselect" 
                    options={pbdPrinciples} 
                    touched={touched} 
                    errors={errors} 
                  />
                </div>
              </div>
              
              <div className="form-row">
                <div className="form-col">
                  <label>Fasi ISO</label>
                  <FormField 
                    name="iso_ids"
                    label="" 
                    type="multiselect" 
                    options={isoPhases} 
                    touched={touched} 
                    errors={errors} 
                  />
                </div>
                
                <div className="form-col">
                  <label>Vulnerabilità</label>
                  <FormField 
                    name="vulnerability_ids"
                    label="" 
                    type="multiselect" 
                    options={vulnerabilities} 
                    touched={touched} 
                    errors={errors} 
                  />
                </div>
              </div>
            </div>
            
            <div className="form-actions">
              <button 
                type="button" 
                className="button secondary" 
                onClick={onCancel}
                disabled={isSubmitting}
              >
                <FaTimes />
                <span>Annulla</span>
              </button>
              <button 
                type="submit" 
                className="button primary" 
                disabled={isSubmitting}
              >
                <FaSave />
                <span>{isSubmitting ? 'Salvataggio...' : (isEdit ? 'Aggiorna Pattern' : 'Crea Pattern')}</span>
              </button>
            </div>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default PatternForm;