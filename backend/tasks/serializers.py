from rest_framework import serializers

class TaskSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    title = serializers.CharField()
    due_date = serializers.DateField()
    estimated_hours = serializers.FloatField()
    importance = serializers.IntegerField(min_value=1, max_value=10)
    dependencies = serializers.ListField(child=serializers.CharField(), required=False)
    
    def validate_dependencies(self, value):
        if value is None:
            return []
        return value