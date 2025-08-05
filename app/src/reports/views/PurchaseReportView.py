class PurchaseReportView(View):

    template_name = 'reports/purchase_report.html'
    def get(self, request, *args, **kwargs):
        # Implement your logic here
        return JsonResponse({"message": "Hello, World!"})
ß