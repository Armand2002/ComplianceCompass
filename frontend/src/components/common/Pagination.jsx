import React from 'react';
import { FaChevronLeft, FaChevronRight } from 'react-icons/fa';

/**
 * Componente per la paginazione
 * @param {Object} props - Props del componente
 * @param {number} props.currentPage - Pagina corrente
 * @param {number} props.totalPages - Numero totale di pagine
 * @param {Function} props.onPageChange - Funzione da chiamare al cambio pagina
 * @param {number} props.totalItems - Numero totale di elementi
 * @param {number} props.pageSize - Dimensione della pagina
 * @param {Function} props.onPageSizeChange - Funzione da chiamare al cambio dimensione pagina
 */
const Pagination = ({ 
  currentPage, 
  totalPages, 
  onPageChange, 
  totalItems, 
  pageSize, 
  onPageSizeChange 
}) => {
  // Calcola gli elementi visualizzati
  const startItem = totalItems === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, totalItems);
  
  // Genera array di pagine da visualizzare
  const getPageNumbers = () => {
    const maxPages = 5; // Numero massimo di pagine da mostrare
    
    if (totalPages <= maxPages) {
      // Se ci sono poche pagine, mostra tutte
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }
    
    // Altrimenti, mostra un range centrato sulla pagina corrente
    const range = Math.floor(maxPages / 2);
    
    let start = currentPage - range;
    let end = currentPage + range;
    
    // Aggiusta i limiti
    if (start < 1) {
      end += (1 - start);
      start = 1;
    }
    
    if (end > totalPages) {
      start -= (end - totalPages);
      end = totalPages;
    }
    
    start = Math.max(start, 1);
    
    return Array.from({ length: end - start + 1 }, (_, i) => i + start);
  };
  
  // Dimensioni di pagina disponibili
  const pageSizeOptions = [10, 25, 50, 100];
  
  return (
    <div className="pagination">
      <div className="pagination-info">
        {totalItems > 0 ? (
          <span>
            Mostrati {startItem}-{endItem} di {totalItems} elementi
          </span>
        ) : (
          <span>Nessun elemento trovato</span>
        )}
      </div>
      
      <div className="pagination-controls">
        {/* Pulsante "Precedente" */}
        <button 
          className="pagination-button prev"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
        >
          <FaChevronLeft />
        </button>
        
        {/* Pagine */}
        <div className="pagination-pages">
          {getPageNumbers().map(page => (
            <button
              key={page}
              className={`pagination-button page ${page === currentPage ? 'active' : ''}`}
              onClick={() => onPageChange(page)}
            >
              {page}
            </button>
          ))}
        </div>
        
        {/* Pulsante "Successivo" */}
        <button 
          className="pagination-button next"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages || totalPages === 0}
        >
          <FaChevronRight />
        </button>
      </div>
      
      <div className="pagination-size">
        <span>Elementi per pagina:</span>
        <select 
          value={pageSize}
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
        >
          {pageSizeOptions.map(size => (
            <option key={size} value={size}>
              {size}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default Pagination;