import React, { useState, useEffect } from "react";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./Income.css";
import { useNavigate, NavLink } from "react-router-dom";
import { formatIndianCurrency } from "../../utils/utils";
import DataTable from "../../components/DataTable";
import Layout from "../../components/Layout";
import Form from "../../components/Form";
import DeleteConfirm from "../../components/DeleteConfirm";
import LoadingOverlay from "../../components/LoadingOverlay";
import api from "../../utils/api";
import { getCookie, removeCookie } from "../../utils/cookies";

function Income() {
  const [incomes, setIncomes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [formData, setFormData] = useState({
    source: "",
    amount: "",
    description: "",
    income_date: "",
  });

  const [errors, setErrors] = useState({
    source: "",
    amount: "",
    description: "",
    income_date: "",
  });

  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(5);
  const [sortConfig, setSortConfig] = useState({ key: "id", direction: "asc" });
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deleteId, setDeleteId] = useState(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const navigate = useNavigate();

  const sidebarLinks = [
    { href: "/dashboard", label: "Dashboard" },
    { href: "/income", label: "Income" },
    { href: "/expense", label: "Expense" },
  ];

  const handleLogout = () => {
    removeCookie("access_token");
    navigate("/signin");
  };

  const fetchIncomes = async () => {
    const token = getCookie("access_token");
    if (!token) {
      toast.error("No access token found.");
      setLoading(false);
      return;
    }

    try {
      const res = await api.get("/income", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const result = res.data;
      if (result.status === "success") setIncomes(result.data);
      else toast.error(result.message || "Failed to fetch incomes");
    } catch (err) {
      toast.error("Error fetching data: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncomes();
  }, []);

  if (loading) return <div className="homepage">Loading...</div>;

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    let processedValue = value;
    if (name === "description" && value.length > 150) {
      processedValue = value.substring(0, 150);
    }
    setFormData({ ...formData, [name]: processedValue });
    if (errors[name]) {
      setErrors({ ...errors, [name]: "" });
    }
  };

  const validateField = (name, value) => {
    let error = "";
    switch (name) {
      case "source":
        if (!value.trim()) error = "Source is required";
        break;
      case "amount":
        if (!value || parseFloat(value) <= 0) error = "Amount must be > 0";
        break;
      case "description":
        if (value.length > 150) error = "Description must be 150 characters or less";
        break;
      case "income_date":
        if (!value) error = "Date is required";
        break;
      default:
        break;
    }
    setErrors((prevErrors) => ({ ...prevErrors, [name]: error }));
  };

  const validateForm = () => {
    validateField("source", formData.source);
    validateField("amount", formData.amount);
    validateField("income_date", formData.income_date);
    return !Object.values(errors).some((error) => error);
  };



  const handleEdit = (income) => {
    setFormData({
      id: income.id,
      source: income.source,
      amount: income.amount,
      description: income.description,
      income_date: income.income_date,
    });
    setErrors({ source: "", amount: "", description: "", income_date: "" });
    setEditingId(income.id);
    setShowForm(true);
  };

  const handleDeleteClick = (id) => {
    setDeleteId(id);
    setDeleteModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    const token = getCookie("access_token");
    if (!token) {
      toast.error("No access token found.");
      return;
    }

    setIsDeleting(true);
    try {
      const response = await api.delete(`/income/${deleteId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const result = response.data;
      if (result.status === "success") {
        setIncomes(incomes.filter((inc) => inc.id !== deleteId));
        toast.success("Income deleted!");
      } else {
        toast.error(result.message || "Failed to delete income");
      }
    } catch (err) {
      toast.error("Error deleting income: " + err.message);
    } finally {
      setIsDeleting(false);
      setDeleteModalOpen(false);
      setDeleteId(null);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteModalOpen(false);
    setDeleteId(null);
  };

  const resetForm = () => {
    setFormData({ source: "", amount: "", description: "", income_date: "" });
    setErrors({ source: "", amount: "", description: "", income_date: "" });
    setEditingId(null);
    setShowForm(false);
  };

  const handleFormSubmitWrapper = async (data) => {
    const token = getCookie("access_token");
    if (!token) {
      toast.error("No access token found.");
      return;
    }

    const url = editingId
      ? `/income/${editingId}`
      : "/income";

    setIsUpdating(true);
    const startTime = Date.now();
    try {
      const config = {
        headers: { Authorization: `Bearer ${token}` },
      };
      const response = editingId
        ? await api.put(url, data, config)
        : await api.post(url, data, config);
      const result = response.data;
      if (result.status === "success") {
        if (editingId) {
          setIncomes(
            incomes.map((inc) => (inc.id === editingId ? result.data : inc))
          );
          toast.success("Income updated!");
        } else {
          setIncomes([...incomes, result.data]);
          toast.success("Income added!");
        }
        resetForm();
      } else {
        toast.error(result.message || "Failed to save income");
      }
    } catch (err) {
      toast.error("Error saving income: " + err.message);
    } finally {
      const elapsed = Date.now() - startTime;
      const minDelay = 500; // Minimum 500ms to ensure visibility
      setTimeout(() => setIsUpdating(false), Math.max(0, minDelay - elapsed));
    }
  };

  const columns = [
    { key: 'id', label: 'ID', sortable: true },
    { key: 'source', label: 'Source', sortable: true },
    { key: 'amount', label: 'Amount', sortable: true, format: (value) => `₹${formatIndianCurrency(value)}` },
    { key: 'description', label: 'Description', sortable: true },
    { key: 'income_date', label: 'Date', sortable: true },
    { key: 'actions', label: 'Actions', sortable: false }
  ];

  const fields = [
    { name: "source", label: "Source", type: "text", required: true },
    { name: "amount", label: "Amount", type: "number", required: true },
    { name: "description", label: "Description", type: "text", required: true },
    { name: "income_date", label: "Date", type: "date", required: true },
  ];

return (
    <Layout title="Income Management" sidebarLinks={sidebarLinks}>
      <ToastContainer position="top-right" autoClose={3000} />

      {!showForm && (
        <button className="btn-primaryss" onClick={() => setShowForm(true)}>
          Create Income
        </button>
      )}
      {showForm && (
        <button className="btn-secondaryss" onClick={resetForm}>
          Cancel
        </button>
      )}

      {showForm && (
        <Form
          fields={fields}
          initialData={formData}
          onSubmit={handleFormSubmitWrapper}
          validateField={validateField}
          submitLabel={editingId ? "Update Income" : "Add Income"}
          onCancel={resetForm}
        />
      )}

      {!showForm && (
        <DataTable
          data={incomes}
          columns={columns}
          onEdit={handleEdit}
          onDelete={handleDeleteClick}
          currentPage={currentPage}
          setCurrentPage={setCurrentPage}
          itemsPerPage={itemsPerPage}
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          sortConfig={sortConfig}
          setSortConfig={setSortConfig}
          isUpdating={isUpdating}
          isDeleting={isDeleting}
        />
      )}

      <DeleteConfirm
        isOpen={deleteModalOpen}
        onClose={handleDeleteCancel}
        onConfirm={handleDeleteConfirm}
        itemName="income"
      />
      <LoadingOverlay isVisible={isUpdating || isDeleting} />
    </Layout>
  );
}

export default Income;
