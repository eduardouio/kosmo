class CollectionsReportsView(View):
    template_name = 'reports/collections_report.html'
    def get(self, request, *args, **kwargs):
        # Implement your logic here
        return JsonResponse({"message": "Hello, World!"})