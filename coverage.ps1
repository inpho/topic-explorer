function Test-Url($url, $response) {
    Try{
        $resp = (Invoke-WebRequest $url | Select-Object -ExpandProperty StatusCode)
    } Catch {
        $resp = $_.Exception.Response.StatusCode.value__
    }
    Write-Host ($url,"(Expected:",$response,"Returned:",$resp,")") -Separator " "
    $resp -eq $response
}

Test-Url "http://localhost:8000/" 200
Test-Url "http://localhost:8000/20/" 200
Test-Url "http://localhost:8000/50/" 400
Test-Url "http://localhost:8000/topics" 200
Test-Url "http://localhost:8000/docs.json" 200
Test-Url "http://localhost:8000/docs.json?random=1" 200
Test-Url "http://localhost:8000/docs.json?q=bush" 200
Test-Url "http://localhost:8000/docs.json?id=AP900817-0118" 200
Test-Url "http://localhost:8000/20/topics.json" 200
Test-Url "http://localhost:8000/topics.json?q=bush|israel" 200
Test-Url "http://localhost:8000/topics.json?q=foobar" 404
Test-Url "http://localhost:8000/topics.json?q=a|the" 410
Test-Url "http://localhost:8000/20/topics/1.json" 200
Test-Url "http://localhost:8000/20/topics/1.json?n=-20" 200
Test-Url "http://localhost:8000/topics.json?q=bush" 200
Test-Url "http://localhost:8000/cluster.csv" 200
Test-Url "http://localhost:8000/20/word_docs.json" 400
Test-Url "http://localhost:8000/20/word_docs.json?q=bush" 200
Test-Url "http://localhost:8000/20/docs_topics/AP900817-0118.json" 200
Test-Url "http://localhost:8000/20/doc_topics/AP900817-0118" 200
Test-Url "http://localhost:8000/20/docs/AP900817-0118" 200
Test-Url "http://localhost:8000/fulltext/AP900817-0118" 200
Test-Url "http://localhost:8000/icons.js" 200
Test-Url "http://localhost:8000/description.md" 200
