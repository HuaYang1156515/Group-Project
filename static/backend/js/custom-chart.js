(function ($) {
    "use strict";

    $(document).ready(function () {
        loadSaleStatisticsChart();
    });

    function loadSaleStatisticsChart() {
        if ($('#myChart').length) {
            $.ajax({
                url: '/backend/chart_data',
                method: 'GET',
                success: function (response) {
                    var ctx = document.getElementById('myChart').getContext('2d');
                    var chart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                            datasets: [{
                                label: 'Sales',
                                tension: 0.3,
                                fill: true,
                                backgroundColor: 'rgba(44, 120, 220, 0.2)',
                                borderColor: 'rgba(44, 120, 220)',
                                data: response.sales
                            },
                            {
                                label: 'Visitors',
                                tension: 0.3,
                                fill: true,
                                backgroundColor: 'rgba(4, 209, 130, 0.2)',
                                borderColor: 'rgb(4, 209, 130)',
                                data: response.users
                            },
                            {
                                label: 'Products',
                                tension: 0.3,
                                fill: true,
                                backgroundColor: 'rgba(380, 200, 230, 0.2)',
                                borderColor: 'rgb(380, 200, 230)',
                                data: response.products
                            }]
                        },
                        options: {
                            plugins: {
                                legend: {
                                    labels: {
                                        usePointStyle: true,
                                    },
                                }
                            }
                        }
                    });
                    // Call the second function after the first AJAX request is complete
                    loadAreaStatisticsChart();
                },
                error: function (xhr, status, error) {
                    console.error("Failed to retrieve chart data", error);
                }
            });
        }
    }

    function loadAreaStatisticsChart() {
        if ($('#myChart2').length) {
            $.ajax({
                url: '/backend/area_data',
                method: 'GET',
                success: function (response) {
                    var ctx = document.getElementById("myChart2");
                    var myChart = new Chart(ctx, {
                        type: 'bar',
                        data: {
                           
                            datasets: [
                                {
                                    label: "USA",
                                    backgroundColor: "#5897fb",
                                    barThickness: 10,
                                    data: response.USA
                                },
                                {
                                    label: "Europe",
                                    backgroundColor: "#7bcf86",
                                    barThickness: 10,
                                    data: response.EU
                                },
                                {
                                    label: "Australia",
                                    backgroundColor: "#ff9076",
                                    barThickness: 10,
                                    data: response.AU
                                },
                                {
                                    label: "New Zealand",
                                    backgroundColor: "#d595e5",
                                    barThickness: 10,
                                    data: response.NZ
                                },
                            ]
                        },
                        options: {
                            plugins: {
                                legend: {
                                    labels: {
                                        usePointStyle: true,
                                    },
                                }
                            }
                        }
                    });
                },
                error: function (xhr, status, error) {
                    console.error("Failed to retrieve area data", error);
                }
            });
        }
    }

})(jQuery);
