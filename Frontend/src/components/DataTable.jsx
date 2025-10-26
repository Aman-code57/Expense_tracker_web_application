import React from 'react';
import { RiDeleteBin6Line } from "react-icons/ri";
import { FaRegEdit } from "react-icons/fa";
import LoadingOverlay from './LoadingOverlay';
import "./datatable.css";

const DataTable = ({
  data,
  columns,
  onEdit,
  onDelete,
  currentPage,
  setCurrentPage,
  itemsPerPage,
  searchTerm,
  setSearchTerm,
  sortConfig,
  setSortConfig,
  tableClass = 'custom-tabled',
  isUpdating = false,
  isDeleting = false
}) => {
  const filteredData = data.filter((item) =>
    columns.some((col) =>
      col.key !== 'actions' &&
      item[col.key]?.toString().toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  const sortedData = [...filteredData].sort((a, b) => {
    if (a[sortConfig.key] < b[sortConfig.key])
      return sortConfig.direction === 'asc' ? -1 : 1;
    if (a[sortConfig.key] > b[sortConfig.key])
      return sortConfig.direction === 'asc' ? 1 : -1;
    return 0;
  });

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentData = sortedData.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(sortedData.length / itemsPerPage);

  const paginate = (pageNumber) => {
    if (pageNumber >= 1 && pageNumber <= totalPages) {
      setCurrentPage(pageNumber);
    }
  };

  const handleSort = (key) => {
    if (!columns.find(col => col.key === key)?.sortable) return;
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') direction = 'desc';
    setSortConfig({ key, direction });
  };

  const renderPagination = () => {
    const pages = [];
    const lastPage = totalPages;

    for (let i = 1; i <= totalPages; i++) {
      // Show first, last, current, and neighbors of current
      if (
        i === 1 ||
        i === lastPage ||
        (i >= currentPage - 1 && i <= currentPage + 1)
      ) {
        pages.push(i);
      } else if (pages[pages.length - 1] !== '...') {
        pages.push('...');
      }
    }

    return pages.map((page, index) =>
      page === '...' ? (
        <span key={index} className="dots">...</span>
      ) : (
        <button
          key={index}
          onClick={() => paginate(page)}
          className={currentPage === page ? 'active' : ''}
        >
          {page}
        </button>
      )
    );
  };

  return (
    <>
      <div className="search-container">
        <input
          type="text"
          placeholder="Search..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="table-containers">
        <table className={tableClass}>
          <thead>
            <tr>
              {columns.map((col, idx) => (
                <th
                  key={idx}
                  onClick={() => handleSort(col.key)}
                  style={{ cursor: col.sortable ? 'pointer' : 'default' }}
                >
                  {col.label}{' '}
                  {sortConfig.key === col.key ? (sortConfig.direction === 'asc' ? '▲' : '▼') : ''}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {currentData.length === 0 ? (
              <tr>
                <td colSpan={columns.length} style={{ textAlign: 'center' }}>
                  No data
                </td>
              </tr>
            ) : (
              currentData.map((item, idx) => (
                <tr key={item.id || idx}>
                  {columns.map((col, i) => (
                    <td key={i}>
                      {col.key === 'actions' ? (
                        <div className="actions">
                          <button className="btn-edit" onClick={() => onEdit(item)} disabled={isUpdating}>
                            <FaRegEdit />
                          </button>
                          <button className="btn-delete" onClick={() => onDelete(item.id)} disabled={isDeleting}>
                            <RiDeleteBin6Line />
                          </button>
                        </div>
                      ) : col.format ? (
                        col.format(item[col.key])
                      ) : (
                        item[col.key]
                      )}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="pagination">
          <button
            onClick={() => paginate(currentPage - 1)}
            disabled={currentPage === 1}
            className="pagination-btn"
          >
            Previous
          </button>

          {renderPagination()}

          <button
            onClick={() => paginate(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="pagination-btn"
          >
            Next
          </button>
        </div>
      )}

      <LoadingOverlay isVisible={isUpdating || isDeleting} />
    </>
  );
};

export default DataTable;
