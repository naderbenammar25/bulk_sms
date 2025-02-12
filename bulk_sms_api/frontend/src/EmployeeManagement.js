import React, { useState, useEffect } from 'react';
import axios from 'axios';

const EmployeeManagement = () => {
    const [employees, setEmployees] = useState([]);

    useEffect(() => {
        axios.get('/api/employees/')
            .then(response => {
                setEmployees(response.data);
            })
            .catch(error => {
                console.error('There was an error fetching the employees!', error);
            });
    }, []);

    const toggleStatus = (id) => {
        axios.post(`/api/employees/${id}/toggle_status/`)
            .then(response => {
                setEmployees(employees.map(emp => emp.id === id ? response.data : emp));
            })
            .catch(error => {
                console.error('There was an error toggling the status!', error);
            });
    };

    return (
        <div>
            <h1>Gestion des Employés</h1>
            <table>
                <thead>
                    <tr>
                        <th>Nom Complet</th>
                        <th>Email</th>
                        <th>Statut</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {employees.map(employee => (
                        <tr key={employee.id}>
                            <td>{employee.first_name} {employee.last_name}</td>
                            <td>{employee.email}</td>
                            <td>{employee.is_active ? 'Actif' : 'Inactif'}</td>
                            <td>
                                <button onClick={() => toggleStatus(employee.id)}>
                                    {employee.is_active ? 'Désactiver' : 'Activer'}
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default EmployeeManagement;